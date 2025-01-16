import streamlit as st
import pandas as pd
import os
import datetime



#Função para exibir a imagem da COBATA
def exibir_imagem():
    imagem_path = "B:\CBT-BKADM\GABRIEL\Gabriel Arquivos ADM\VSCODE\PROJETO COBATA\Arquivos\WhatsApp_Image_2024-11-28_at_10.47.28-removebg-preview.png"
    if os.path.exists(imagem_path):
        st.image(imagem_path, caption= "", width=200, use_container_width=False)
    else:
        st.error("Imagem não foi encontrada!")




#Função do Corpo
def main():
    st.title("Análise de Validade dos Produtos")

    exibir_imagem()

    

if __name__ == "__main__":
    main()



