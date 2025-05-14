import streamlit as st
from collections import deque, defaultdict
import itertools

def parse_grammar(input_text):
    """
    Convierte el texto ingresado en formato:
      D → DA | DE | b | CA | DD | a
      E → AD
      ...
    a un diccionario {no_terminal: [producciones]}.
    Se admite tanto el símbolo "→" como "->".
    """
    grammar = defaultdict(list)
    # Reemplaza flechas y procesa cada línea
    input_text = input_text.replace("→", "->").replace("ε", "*")
    for line in input_text.strip().split('\n'):
        if '->' in line:
            head, prods = line.split("->", 1)
            head = head.strip()
            for prod in prods.split('|'):
                prod = prod.strip()
                if prod:
                    grammar[head].append(prod)
    
    # Eliminar posibles producciones duplicadas
    for nt in grammar:
        grammar[nt] = list(set(grammar[nt]))
    
    return dict(grammar)

def generate_strings(grammar, start, max_depth=7, max_len=15):
    """
    Genera, de forma aproximada, el conjunto de cadenas terminales (sin no terminales)
    derivables a partir del símbolo start hasta max_depth o max_len.
    Se asume que:
      - Las producciones son cadenas de símbolos.
      - Los símbolos no terminales son letras mayúsculas.
      - El símbolo '*' o 'ε' representa epsilon (cadena vacía).
    """
    resultados = set()
    # Cada elemento es una tupla: (cadena_actual, profundidad)
    cola = deque([(start, 0)])
    visited = set()
    
    while cola:
        derivacion, profundidad = cola.popleft()
        
        # Si la derivación es muy larga o ya fue visitada, saltamos
        if len(derivacion) > max_len or derivacion in visited:
            continue
            
        visited.add(derivacion)
        
        # Si la cadena es terminal, la agregamos a los resultados
        if all(not c.isupper() for c in derivacion):
            cadena = derivacion.replace('*', '')
            resultados.add(cadena)
            continue
        
        # Si alcanzamos el máximo de profundidad, no continuamos derivando
        if profundidad >= max_depth:
            continue
        
        # Buscar el primer no terminal en la cadena
        for i, simbolo in enumerate(derivacion):
            if simbolo.isupper():
                nt = simbolo
                break
        else:
            # Este caso nunca debería ocurrir aquí debido al check anterior
            continue
        
        # Si no existen producciones para el no terminal, se omite esta derivación
        if nt not in grammar:
            continue
        
        # Expande reemplazando el no terminal encontrado por cada producción
        for prod in grammar[nt]:
            nueva_derivacion = derivacion[:i] + prod + derivacion[i+1:]
            cola.append((nueva_derivacion, profundidad+1))
            
    return resultados


def find_non_terminals(grammar):
    """Retorna el conjunto de símbolos no terminales de la gramática."""
    return set(grammar.keys())

def find_terminal_symbols(grammar):
    """Retorna el conjunto aproximado de símbolos terminales de la gramática."""
    terminals = set()
    for prods in grammar.values():
        for prod in prods:
            for c in prod:
                if not c.isupper() and c != '*':
                    terminals.add(c)
    return terminals

def analyze_grammar_structure(grammar):
    """Analiza la estructura de la gramática para ayudar a encontrar mapeos entre gramáticas."""
    non_terminals = find_non_terminals(grammar)
    
    # Características por no terminal
    features = {}
    
    for nt in non_terminals:
        # Contar tipo de producciones
        num_epsilon = 0
        num_terminals = 0
        num_nt_only = 0
        num_mixed = 0
        terminal_positions = defaultdict(int)
        
        for prod in grammar[nt]:
            has_terminal = False
            has_nonterminal = False
            
            if prod == '*':
                num_epsilon += 1
                continue
                
            for i, c in enumerate(prod):
                if c.isupper():
                    has_nonterminal = True
                elif c != '*':
                    has_terminal = True
                    terminal_positions[c] += 1
            
            if has_terminal and not has_nonterminal:
                num_terminals += 1
            elif has_nonterminal and not has_terminal:
                num_nt_only += 1
            elif has_terminal and has_nonterminal:
                num_mixed += 1
        
        features[nt] = {
            'num_prods': len(grammar[nt]),
            'num_epsilon': num_epsilon,
            'num_terminals': num_terminals,
            'num_nt_only': num_nt_only,
            'num_mixed': num_mixed,
            'terminal_positions': terminal_positions
        }
    
    return features

def try_symbol_mappings(grammar1, grammar2, start1, start2, max_depth=5):
    """
    Intenta encontrar un mapeo entre los símbolos no terminales de las dos gramáticas
    que haga que ambas generen el mismo lenguaje.
    """
    nts1 = find_non_terminals(grammar1)
    nts2 = find_non_terminals(grammar2)
    
    # Si tienen diferente número de no terminales, sería más complejo encontrar un mapeo directo
    if len(nts1) != len(nts2):
        st.warning(f"Las gramáticas tienen diferente número de no terminales: {len(nts1)} vs {len(nts2)}. " 
                  f"Aún es posible que sean equivalentes pero el mapeo será más difícil de encontrar.")
    
    # Analizamos las características estructurales para ayudar a encontrar mapeos
    features1 = analyze_grammar_structure(grammar1)
    features2 = analyze_grammar_structure(grammar2)
    
    # Primero intentamos mapear los símbolos iniciales
    possible_mappings = [{start1: start2}]
    
    # Para gramáticas pequeñas, podemos intentar múltiples mapeos
    if len(nts1) <= 6:  # Limitamos las permutaciones para gramáticas grandes
        # Excluimos el símbolo inicial que ya está mapeado
        other_nts1 = [nt for nt in nts1 if nt != start1]
        other_nts2 = [nt for nt in nts2 if nt != start2]
        
        # Generar todas las permutaciones posibles de mapeos para los no terminales restantes
        for perm in itertools.permutations(other_nts2, len(other_nts1)):
            mapping = {start1: start2}
            for i, nt in enumerate(other_nts1):
                mapping[nt] = perm[i]
            
            # Aplicar este mapeo a la gramática 1
            mapped_grammar = apply_mapping(grammar1, mapping)
            
            # Comparar las cadenas generadas
            gen1 = generate_strings(mapped_grammar, start2, max_depth)
            gen2 = generate_strings(grammar2, start2, max_depth)
            
            if gen1 == gen2:
                return mapping
    
    return None

def apply_mapping(grammar, mapping):
    """Aplica un mapeo de símbolos no terminales a una gramática."""
    new_grammar = defaultdict(list)
    
    for nt, prods in grammar.items():
        # Mapear el no terminal actual
        if nt in mapping:
            new_nt = mapping[nt]
        else:
            new_nt = nt
            
        for prod in prods:
            new_prod = ""
            for c in prod:
                if c.isupper() and c in mapping:
                    new_prod += mapping[c]
                else:
                    new_prod += c
            new_grammar[new_nt].append(new_prod)
    
    # Eliminar duplicados en las producciones mapeadas
    for nt in new_grammar:
        new_grammar[nt] = list(set(new_grammar[nt]))
    
    return dict(new_grammar)

def check_equivalence(grammar1, grammar2, start1, start2, max_depth=7, max_len=15):
    """
    Compara (aproximadamente) dos gramáticas generando cadenas terminales hasta max_depth.
    También intenta encontrar un mapeo entre los símbolos no terminales.
    """
    # Primero hacemos la comparación directa con configuraciones predeterminadas
    gen1 = generate_strings(grammar1, start1, max_depth, max_len)
    gen2 = generate_strings(grammar2, start2, max_depth, max_len)
    
    st.markdown("### Cadenas generadas - Gramática 1")
    st.code("\n".join(sorted(gen1)))
    st.markdown("### Cadenas generadas - Gramática 2")
    st.code("\n".join(sorted(gen2)))
    
    if gen1 == gen2:
        st.success("Las gramáticas parecen equivalentes hasta la profundidad y longitud indicadas.")
        return True
    
    # Si la comparación directa no funciona, intentamos encontrar un mapeo
    st.info("Las gramáticas no coinciden directamente. Intentando buscar un mapeo de símbolos...")
    
    mapping = try_symbol_mappings(grammar1, grammar2, start1, start2, max_depth)
    
    if mapping:
        st.success("Se encontró un mapeo de símbolos que hace equivalentes las gramáticas:")
        st.write(mapping)
        
        # Aplicar el mapeo y verificar
        mapped_grammar = apply_mapping(grammar1, mapping)
        gen1_mapped = generate_strings(mapped_grammar, start2, max_depth, max_len)
        
        st.markdown("### Cadenas generadas - Gramática 1 (con mapeo)")
        st.code("\n".join(sorted(gen1_mapped)))
        
        if gen1_mapped == gen2:
            st.success("Las gramáticas son equivalentes con el mapeo encontrado.")
            return True
        else:
            st.error("Las gramáticas NO son equivalentes incluso con el mapeo encontrado.")
            
            # Mostrar diferencias
            st.markdown("### Diferencias encontradas:")
            st.markdown("En G1 pero no en G2:")
            st.code("\n".join(sorted(gen1_mapped - gen2)))
            st.markdown("En G2 pero no en G1:")
            st.code("\n".join(sorted(gen2 - gen1_mapped)))
            
            return False
    else:
        st.error("Las gramáticas NO son equivalentes para la profundidad indicada.")
        
        # Mostrar diferencias
        st.markdown("### Diferencias encontradas:")
        st.markdown("En G1 pero no en G2:")
        st.code("\n".join(sorted(gen1 - gen2)))
        st.markdown("En G2 pero no en G1:")
        st.code("\n".join(sorted(gen2 - gen1)))
        
        return False
def main():
    st.set_page_config(page_title="Grammar Checker", page_icon="🔤", layout="wide")
    st.title("Grammar Checker: Verificación de Equivalencia de Gramáticas")
    
    st.markdown("Ingresa las dos gramáticas a comparar. Cada producción debe estar en una línea, usando:")
    st.markdown("- `→` o `->` para separar cabeza y producciones")
    st.markdown("- `|` para separar alternativas")
    st.markdown("- `*` o `ε` para representar epsilon (cadena vacía)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Gramática 1")
        grammar1_text = st.text_area("Gramática 1:", height=200, value="""D → DA | DE | b | CA | DD | a
E → AD
S → DA | * | DS | DE | b | CA | DD | a
C → b
A → a | DA | DE | DD""")
        start_symbol1 = st.text_input("Símbolo inicial gramática 1", value="S")
    
    with col2:
        st.subheader("Gramática 2")
        grammar2_text = st.text_area("Gramática 2:", height=200, value="""S → ES | EA | FA | EE | b | GE | GD | ED | a | *
A → GE | GD | EE | ED | EA | a
D → FA | EE | b | GE | GD | ED | EA | a
E → a
F → b
G → EA""")
        start_symbol2 = st.text_input("Símbolo inicial gramática 2", value="S")
    
    # Opción para mostrar configuraciones avanzadas
    show_advanced = st.checkbox("Mostrar configuraciones avanzadas")
    
    # Valores predeterminados
    max_depth = 10  # Aumentamos el valor predeterminado para mayor precisión
    max_len = 20    # Aumentamos el valor predeterminado para cadenas más largas
    
    if show_advanced:
        col1, col2 = st.columns(2)
        with col1:
            max_depth = st.slider("Profundidad máxima de derivación", min_value=3, max_value=15, value=10)
        with col2:
            max_len = st.slider("Longitud máxima de cadena", min_value=5, max_value=30, value=20)
    
    if st.button("Comparar Gramáticas", type="primary"):
        try:
            with st.spinner("Procesando gramáticas..."):
                grammar1 = parse_grammar(grammar1_text)
                grammar2 = parse_grammar(grammar2_text)
                
                # Calculamos automáticamente los parámetros según el tamaño de las gramáticas
                if not show_advanced:
                    # Ajustamos profundidad según el número de no terminales
                    num_nts1 = len(find_non_terminals(grammar1))
                    num_nts2 = len(find_non_terminals(grammar2))
                    avg_nts = (num_nts1 + num_nts2) / 2
                    
                    # Calculamos la complejidad media de producciones
                    avg_prod_len1 = calc_avg_prod_length(grammar1)
                    avg_prod_len2 = calc_avg_prod_length(grammar2)
                    
                    # Ajustamos los parámetros automáticamente
                    max_depth = min(15, max(7, int(10 + (5 - avg_nts))))
                    max_len = min(30, max(10, int(5 * avg_nts)))
                    
                    st.info(f"Configuración automática: Profundidad máxima = {max_depth}, Longitud máxima = {max_len}")
                
                # Verificar si hay símbolos duplicados
                for nt in grammar2:
                    if grammar2_text.count(f"{nt} →") > 1 or grammar2_text.count(f"{nt}→") > 1:
                        st.warning(f"La gramática 2 tiene producciones duplicadas para el símbolo {nt}. Se han combinado.")
                
                st.markdown("## Resultados de la comprobación")
                check_equivalence(grammar1, grammar2, start_symbol1, start_symbol2, max_depth, max_len)
        except Exception as e:
            st.error(f"Error al procesar las gramáticas: {e}")
            st.exception(e)

def calc_avg_prod_length(grammar):
    """Calcula la longitud promedio de las producciones en la gramática."""
    total_len = 0
    count = 0
    
    for prods in grammar.values():
        for prod in prods:
            if prod != '*':  # Ignoramos epsilon en el cálculo
                total_len += len(prod)
                count += 1
    
    return total_len / max(1, count)  # Evitar división por cero

main()