import streamlit as st

def redes_socias():
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)
    css_code = """
    body {
    margin: 0;
    padding: 0;
    background: #f1f1f1;
    }
    .s-m {
    margin: 3px auto;
    display: flex;
    max-width: 700px;
    gap: 10px; 
    }
    .s-m a {
    text-decoration: none;
    font-size: 15px; 
    color: #f1f1f1;
    width: 40px; 
    height: 40px; 
    text-align: center;
    transition: 0.4s all;
    line-height: 40px;
    cursor: pointer;
    background: #314652;
    border-radius: 50%;
    }
    .s-m a:hover {
    transform: scale(1.5); 
    }

        """

    # Adicione o HTML para os botões
    html_code = """
    <div class="s-m">
    <a class="fab fa-instagram" href="https://www.instagram.com/ladslopes/"></a>
    <a class="fab fa-github" href="https://github.com/LadislauLopes" ></a>
    <a class="fab fa-whatsapp" href="https://wa.me/68999328239"></a>
    <a class="fab fa-linkedin-in" href="https://www.linkedin.com/in/ladislaulopes/"></a>
    </div>
    """

    # Renderize o CSS e o HTML no Streamlit
    st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
    st.markdown(html_code, unsafe_allow_html=True)
