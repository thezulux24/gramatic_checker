import streamlit as st
from collections import deque, defaultdict
import itertools

# funcion para parsear el texto de entrada y devolver un diccionario de producciones
def parse_grammar(input_text):
    """
    convierte el texto ingresado en formato:
      d -> da | de | b | ca | dd | a
      e -> ad
      ...
    a un diccionario {no_terminal: [producciones]}.
    admite tanto el simbolo "->" como "→".
    """
    grammar = defaultdict(list)
    # reemplaza las flechas y epsilon para homogeneizar
    input_text = input_text.replace("→", "->").replace("ε", "*")
    # procesa cada linea del texto
    for line in input_text.strip().split('\n'):
        if '->' in line:
            # separa la cabeza y las producciones
            head, prods = line.split("->", 1)
            head = head.strip()  # limpia espacios
            # separa las alternativas segun el caracter |
            for prod in prods.split('|'):
                prod = prod.strip()
                if prod:
                    grammar[head].append(prod)
    
    # elimina posibles producciones duplicadas en cada no terminal
    for nt in grammar:
        grammar[nt] = list(set(grammar[nt]))
    
    return dict(grammar)

# funcion para generar cadenas terminales aproximadas a partir de la gramatica
def generate_strings(grammar, start, max_depth=7, max_len=15):
    """
    genera de forma aproximada el conjunto de cadenas terminales (sin no terminales)
    derivables del simbolo start, hasta una profundidad maxima o longitud maxima.
    asume que:
      - las producciones son cadenas de simbolos.
      - los simbolos no terminales son letras mayusculas.
      - '*' o 'ε' representan epsilon (cadena vacia).
    """
    resultados = set()
    # la cola almacena tuplas de (cadena, profundidad)
    cola = deque([(start, 0)])
    visited = set()
    
    while cola:
        derivacion, profundidad = cola.popleft()
        
        # si la cadena es muy larga o ya se proceso, se salta
        if len(derivacion) > max_len or derivacion in visited:
            continue
            
        visited.add(derivacion)
        
        # si todos los simbolos son terminales, se agrega la cadena resultado
        if all(not c.isupper() for c in derivacion):
            # remueve el simbolo de epsilon
            cadena = derivacion.replace('*', '')
            resultados.add(cadena)
            continue
        
        # si se alcanzo la profundidad maxima, se detiene la derivacion
        if profundidad >= max_depth:
            continue
        
        # busca el primer simbolo no terminal en la derivacion
        for i, simbolo in enumerate(derivacion):
            if simbolo.isupper():
                nt = simbolo
                break
        else:
            # este caso no deberia ocurrir
            continue
        
        # si no hay producciones para el no terminal, se omite esta derivacion
        if nt not in grammar:
            continue
        
        # expande la derivacion reemplazando el no terminal por cada produccion
        for prod in grammar[nt]:
            nueva_derivacion = derivacion[:i] + prod + derivacion[i+1:]
            cola.append((nueva_derivacion, profundidad+1))
            
    return resultados

# funcion para encontrar los simbolos no terminales de la gramatica
def find_non_terminals(grammar):
    # se asume que las claves son los no terminales
    return set(grammar.keys())

# funcion para encontrar aproximadamente los simbolos terminales de la gramatica
def find_terminal_symbols(grammar):
    terminals = set()
    for prods in grammar.values():
        for prod in prods:
            for c in prod:
                # se considera terminal si no es mayuscula y no es epsilon
                if not c.isupper() and c != '*':
                    terminals.add(c)
    return terminals

# funcion para analizar la estructura de la gramatica
def analyze_grammar_structure(grammar):
    """
    analiza la estructura de la gramatica para obtener caracteristicas de cada no terminal.
    se generan contadores de:
      - cantidad de producciones
      - cantidad de producciones con epsilon
      - producciones con solo terminales
      - producciones con solo no terminales
      - producciones mixtas
      - posiciones de terminales
    """
    non_terminals = find_non_terminals(grammar)
    features = {}
    
    for nt in non_terminals:
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

# funcion para intentar encontrar un mapeo entre no terminales de 2 gramaticas
def try_symbol_mappings(grammar1, grammar2, start1, start2, max_depth=5):
    """
    intenta encontrar un mapeo entre los simbolos no terminales de grammar1 y grammar2
    de modo que ambas generen el mismo lenguaje (segun derivaciones aproximadas).
    """
    nts1 = find_non_terminals(grammar1)
    nts2 = find_non_terminals(grammar2)
    
    # si la cantidad de no terminales difiere, el mapeo directo es mas complejo
    if len(nts1) != len(nts2):
        st.warning(f"las gramaticas tienen distinta cantidad de no terminales: {len(nts1)} vs {len(nts2)}. aun es posible que sean equivalentes pero el mapeo sera mas dificil.")
    
    # se obtienen las caracteristicas de cada gramatica (no se usan directamente en este ejemplo)
    features1 = analyze_grammar_structure(grammar1)
    features2 = analyze_grammar_structure(grammar2)
    
    # se intenta mapear primero los simbolos iniciales
    possible_mappings = [{start1: start2}]
    
    # para gramaticas pequenas se prueban multiples mapeos
    if len(nts1) <= 6:
        # se excluye el simbolo inicial que ya esta mapeado
        other_nts1 = [nt for nt in nts1 if nt != start1]
        other_nts2 = [nt for nt in nts2 if nt != start2]
        
        # se generan todas las permutaciones posibles para los no terminales restantes
        for perm in itertools.permutations(other_nts2, len(other_nts1)):
            mapping = {start1: start2}
            for i, nt in enumerate(other_nts1):
                mapping[nt] = perm[i]
            
            # se aplica el mapeo a grammar1
            mapped_grammar = apply_mapping(grammar1, mapping)
            
            # se generan las cadenas derivadas para comparar
            gen1 = generate_strings(mapped_grammar, start2, max_depth)
            gen2 = generate_strings(grammar2, start2, max_depth)
            
            if gen1 == gen2:
                return mapping
    
    return None

# funcion para aplicar un mapeo de simbolos no terminales a una gramatica
def apply_mapping(grammar, mapping):
    """
    aplica el mapeo definido en "mapping" a cada produccion de la gramatica.
    reemplaza los simbolos no terminales segun el mapeo.
    """
    new_grammar = defaultdict(list)
    
    for nt, prods in grammar.items():
        # se asigna el nuevo simbolo para la cabeza
        if nt in mapping:
            new_nt = mapping[nt]
        else:
            new_nt = nt
            
        for prod in prods:
            new_prod = ""
            # se recorre cada simbolo y se aplica el mapeo si es no terminal
            for c in prod:
                if c.isupper() and c in mapping:
                    new_prod += mapping[c]
                else:
                    new_prod += c
            new_grammar[new_nt].append(new_prod)
    
    # se eliminan duplicados en las producciones mapeadas
    for nt in new_grammar:
        new_grammar[nt] = list(set(new_grammar[nt]))
    
    return dict(new_grammar)

# funcion para comprobar (aproximadamente) la equivalencia de 2 gramaticas
def check_equivalence(grammar1, grammar2, start1, start2, max_depth=7, max_len=15):
    """
    compara dos gramaticas generando cadenas terminales hasta una profundidad y longitud determinadas.
    si las cadenas resultantes son iguales, se asume equivalencia.
    si no, se intenta encontrar un mapeo entre los simbolos no terminales.
    """
    # generamos las cadenas derivadas de cada gramatica
    gen1 = generate_strings(grammar1, start1, max_depth, max_len)
    gen2 = generate_strings(grammar2, start2, max_depth, max_len)
    
    st.markdown("### cadenas generadas - gramatica 1")
    st.code("\n".join(sorted(gen1)))
    st.markdown("### cadenas generadas - gramatica 2")
    st.code("\n".join(sorted(gen2)))
    
    if gen1 == gen2:
        st.success("las gramaticas parecen equivalentes hasta la profundidad y longitud indicadas.")
        return True
    
    # si no coinciden, se intenta encontrar un mapeo entre no terminales
    st.info("las gramaticas no coinciden directamente. intentando buscar un mapeo de simbolos...")
    
    mapping = try_symbol_mappings(grammar1, grammar2, start1, start2, max_depth)
    
    if mapping:
        st.success("se encontro un mapeo de simbolos que hace equivalentes las gramaticas:")
        st.write(mapping)
        
        mapped_grammar = apply_mapping(grammar1, mapping)
        gen1_mapped = generate_strings(mapped_grammar, start2, max_depth, max_len)
        
        st.markdown("### cadenas generadas - gramatica 1 (con mapeo)")
        st.code("\n".join(sorted(gen1_mapped)))
        
        if gen1_mapped == gen2:
            st.success("las gramaticas son equivalentes con el mapeo encontrado.")
            return True
        else:
            st.error("las gramaticas no son equivalentes incluso con el mapeo encontrado.")
            
            st.markdown("### diferencias encontradas:")
            st.markdown("en g1 pero no en g2:")
            st.code("\n".join(sorted(gen1_mapped - gen2)))
            st.markdown("en g2 pero no en g1:")
            st.code("\n".join(sorted(gen2 - gen1_mapped)))
            
            return False
    else:
        st.error("las gramaticas no son equivalentes para la profundidad indicada.")
        
        st.markdown("### diferencias encontradas:")
        st.markdown("en g1 pero no en g2:")
        st.code("\n".join(sorted(gen1 - gen2)))
        st.markdown("en g2 pero no en g1:")
        st.code("\n".join(sorted(gen2 - gen1)))
        
        return False

# funcion para calcular la longitud promedio de las producciones en la gramatica
def calc_avg_prod_length(grammar):
    """
    recorre todas las producciones de la gramatica y calcula la longitud promedio,
    ignorando las producciones epsilon.
    """
    total_len = 0
    count = 0
    
    for prods in grammar.values():
        for prod in prods:
            if prod != '*':  # ignoramos epsilon
                total_len += len(prod)
                count += 1
    
    return total_len / max(1, count)  # se evita division por cero

# funcion principal que ejecuta la aplicacion streamlit
def main():
    st.set_page_config(page_title="grammar checker", page_icon="🔤", layout="wide")
    st.title("grammar checker: verificacion de equivalencia de gramaticas")
    
    # instrucciones para el usuario sobre el formato de entrada
    st.markdown("ingresa las dos gramaticas a comparar. cada produccion debe estar en una linea, usando:")
    st.markdown("- `→` o `->` para separar cabeza y producciones")
    st.markdown("- `|` para separar alternativas")
    st.markdown("- `*` o `ε` para representar epsilon (cadena vacia)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("gramatica 1")
        grammar1_text = st.text_area("gramatica 1:", height=200, value="""D → DA | DE | b | CA | DD | a
E → AD
S → DA | * | DS | DE | b | CA | DD | a
C → b
A → a | DA | DE | DD""")
        start_symbol1 = st.text_input("simbolo inicial gramatica 1", value="S")
    
    with col2:
        st.subheader("gramatica 2")
        grammar2_text = st.text_area("gramatica 2:", height=200, value="""S → ES | EA | FA | EE | b | GE | GD | ED | a | *
A → GE | GD | EE | ED | EA | a
D → FA | EE | b | GE | GD | ED | EA | a
E → a
F → b
G → EA""")
        start_symbol2 = st.text_input("simbolo inicial gramatica 2", value="S")
    
    # opcion para mostrar configuraciones avanzadas
    show_advanced = st.checkbox("mostrar configuraciones avanzadas")
    
    # valores predeterminados para derivacion
    max_depth = 10  # mayor profundidad para mayor precision
    max_len = 20    # mayor longitud para cadenas mas largas
    
    if show_advanced:
        col1, col2 = st.columns(2)
        with col1:
            max_depth = st.slider("profundidad maxima de derivacion", min_value=3, max_value=15, value=10)
        with col2:
            max_len = st.slider("longitud maxima de cadena", min_value=5, max_value=30, value=20)
    
    if st.button("comparar gramaticas", type="primary"):
        try:
            with st.spinner("procesando gramaticas..."):
                grammar1 = parse_grammar(grammar1_text)
                grammar2 = parse_grammar(grammar2_text)
                
                # ajuste automatico de parametros si no se muestran opciones avanzadas
                if not show_advanced:
                    num_nts1 = len(find_non_terminals(grammar1))
                    num_nts2 = len(find_non_terminals(grammar2))
                    avg_nts = (num_nts1 + num_nts2) / 2
                    
                    avg_prod_len1 = calc_avg_prod_length(grammar1)
                    avg_prod_len2 = calc_avg_prod_length(grammar2)
                    
                    max_depth = min(15, max(7, int(10 + (5 - avg_nts))))
                    max_len = min(30, max(10, int(5 * avg_nts)))
                    
                    st.info(f"configuracion automatica: profundidad maxima = {max_depth}, longitud maxima = {max_len}")
                
                # advertencia si existen simbolos duplicados en gramatica 2
                for nt in grammar2:
                    if grammar2_text.count(f"{nt} →") > 1 or grammar2_text.count(f"{nt}→") > 1:
                        st.warning(f"la gramatica 2 tiene producciones duplicadas para el simbolo {nt}. se han combinado.")
                
                st.markdown("## resultados de la comprobacion")
                check_equivalence(grammar1, grammar2, start_symbol1, start_symbol2, max_depth, max_len)
        except Exception as e:
            st.error(f"error al procesar las gramaticas: {e}")
            st.exception(e)

main()