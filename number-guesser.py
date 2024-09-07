import streamlit as st
import pandas as pd
import numpy as np

# Funções fornecidas
def populate_dataframe(max_power):
    power_dict = {i: [] for i in range(1, max_power + 1)}
    for num in range(1, (2 ** max_power)):
        powers = powers_of_two(num)
        for power in powers:
            if power <= max_power:
                power_dict[power].append(num)
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in power_dict.items()]))
    return df

def powers_of_two(num):
    powers = []
    power = 0
    while num > 0:
        if num & 1:
            powers.append(power + 1)
        num >>= 1
        power += 1
    return powers

def number_from_powers(powers):
    number = 0
    for power in powers:
        number += 2 ** (power - 1)
    return number

# Application Initialization
if 'max_power' not in st.session_state:
    st.session_state.max_power = 6  # Default value

if 'powers' not in st.session_state:
    st.session_state.powers = []

if 'game_started' not in st.session_state:
    st.session_state.game_started = False

st.title("Matemágica, o Adivinhador de Números!")

if not st.session_state.game_started:
    st.write("Instruções:")
    st.write("1) Escolha o nível de dificuldade;")
    st.write("2) Pense em um número que esteja contido no intervalo indicado.")
    # Allow the user to select the maximum power which determines the number range and question count
    max_power = st.select_slider("Deslize o cursor para selecionar a dificuldade pretendida. Quanto maior a dificuldade, mais perguntas precisarei fazer!", options=range(3, 10), value=st.session_state.max_power)
    st.session_state.max_power = max_power
    max_number = 2**max_power - 1
    st.write(f"Escolha um número entre 1 e {max_number} para que eu o adivinhe.")
    if st.button("Começar o jogo", key="start"):
        st.session_state.game_started = True
        st.session_state.col_index = 0
        st.rerun()
else:
    max_power = st.session_state.max_power
    max_number = 2**max_power - 1

# Populate the dataframe based on the selected max_power
df = populate_dataframe(max_power)

if st.session_state.game_started:
    # Only display progress and question number if the game is still asking questions
    if 'col_index' in st.session_state and st.session_state.col_index < max_power:
        st.write(f"Estamos falando de um número entre 1 e {max_number}...")

        # Display the progress bar
        progress_percentage = st.session_state.col_index / max_power  # This will range from 0 to just below 1
        st.progress(progress_percentage)

        # Show the number of questions answered out of total
        st.write(f"Pergunta {st.session_state.col_index + 1} de {max_power}")

        col_name = st.session_state.col_index + 1
        numbers = df[col_name].dropna().astype(int).tolist()
        
        # Calculate dimensions for the closest square-ish DataFrame
        num_elements = len(numbers)
        size = int(np.ceil(np.sqrt(num_elements)))
        padded_length = size ** 2

        # Pad the list with NaNs to match the required length
        numbers_padded = numbers + [np.nan] * (padded_length - num_elements)
        
        # Convert list to a DataFrame and reshape it
        numbers_df = pd.DataFrame(numbers_padded, columns=['Number'])
        numbers_df = numbers_df['Number'].values.reshape(size, size)
        numbers_df = pd.DataFrame(numbers_df)

        # Use raw HTML to create a table without headers or indices, displaying numbers as integers
        html = "<table>"
        for row in numbers_df.itertuples(index=False):
            html += "<tr>" + "".join(f"<td>{'' if pd.isna(val) else int(val)}</td>" for val in row) + "</tr>"
        html += "</table>"
        
        st.markdown(html, unsafe_allow_html=True)
        st.write("O seu número está presente nesta lista?")

        col_index = st.session_state.col_index
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Sim", key=f"yes_{col_index}"):
                st.session_state.powers.append(col_name)
                st.session_state.col_index = col_index + 1
                st.rerun()
        
        with col2:
            if st.button("Não", key=f"no_{col_index}"):
                st.session_state.col_index = col_index + 1
                st.rerun()

    # Handle the end of the game
    if 'col_index' in st.session_state and st.session_state.col_index >= max_power:
        if not st.session_state.powers:
            st.error(f"Parece que o número que você escolheu não está entre 1 e {max_number}!")
        else:
            chosen_number = number_from_powers(st.session_state.powers)
            st.success(f"O número que você escolheu é: {chosen_number}")
        
        # Hide the progress bar and question counter at the end
        st.write("Jogo concluído!")
        if st.button("Jogar novamente", key="restart"):
            st.session_state.powers = []
            st.session_state.col_index = 0
            st.session_state.game_started = False
            st.rerun()
