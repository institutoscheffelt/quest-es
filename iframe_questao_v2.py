import streamlit as st
import mysql.connector
import streamlit.components.v1 as components
import random
import pandas as pd

# Configurações de conexão
config = {
    'user': 'admin',
    'password': 'Eduardo13*',
    'host': 'institutoscheffelt.ckrs9teerzcf.sa-east-1.rds.amazonaws.com',
    'database': 'questoes',
    'raise_on_warnings': True
}


# Adicione uma função para salvar as respostas do aluno
def salvar_respostas_aluno(questao_id, resposta_usuario, gabarito_oficial, assunto, topico):
    # Salvar as respostas do aluno no estado da sessão
    if "respostas_aluno" not in st.session_state:
        st.session_state.respostas_aluno = {"QuestaoID": [], "RespostaUsuario": [], "GabaritoOficial": [], "Assunto": [], "Topico": [], "RespostaCorreta": []}

    # Verificar se a resposta do aluno está correta
    resposta_correta = resposta_usuario == gabarito_oficial

    st.session_state.respostas_aluno["QuestaoID"].append(questao_id)
    st.session_state.respostas_aluno["RespostaUsuario"].append(resposta_usuario)
    st.session_state.respostas_aluno["GabaritoOficial"].append(gabarito_oficial)
    st.session_state.respostas_aluno["Assunto"].append(assunto)
    st.session_state.respostas_aluno["Topico"].append(topico)
    st.session_state.respostas_aluno["RespostaCorreta"].append(resposta_correta)



# Função para obter a lista de assuntos disponíveis
@st.cache_data
def obter_assuntos_disponiveis(materia):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        query = """
            SELECT DISTINCT Assuntos.Assunto
            FROM Questoes Q
            JOIN Assuntos ON Q.AssuntoID = Assuntos.AssuntoID
            JOIN Materias M ON Q.MateriaID = M.MateriaID
            WHERE M.Materia = %s;
        """
        cursor.execute(query, (materia,))
        assuntos = [row[0] for row in cursor.fetchall()]
        return assuntos

    except Exception as e:
        st.error(f"Erro ao obter assuntos disponíveis: {e}")

    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

@st.cache_data
def obter_topicos_disponiveis(materia):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        query = """
            SELECT DISTINCT Topicos.Topico
            FROM Questoes Q
            JOIN Topicos ON Q.TopicoID = Topicos.TopicoID
            JOIN Materias M ON Q.MateriaID = M.MateriaID
            WHERE M.Materia = %s;
        """
        cursor.execute(query, (materia,))
        topicos = [row[0] for row in cursor.fetchall()]
        return topicos

    except Exception as e:
        st.error(f"Erro ao obter tópicos disponíveis: {e}")

    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()


# Função para obter a quantidade máxima de questões
@st.cache_data
def obter_quantidade_maxima_questoes(materia, assuntos, topicos):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()


        # Consulta SQL com filtro por assuntos específicos
        # Monta a string de placeholders para os assuntos
        placeholders = ', '.join(['%s'] * len(assuntos))
        placeholders_1 = ', '.join(['%s'] * len(topicos))
        query = f"""
            SELECT COUNT(Questoes.QuestaoID) as quantidade
            FROM Questoes
            JOIN Materias ON Questoes.MateriaID = Materias.MateriaID
            JOIN Assuntos ON Questoes.AssuntoID = Assuntos.AssuntoID
            JOIN Topicos ON Questoes.TopicoID = Topicos.TopicoID
            WHERE Materias.Materia = %s
            AND Assuntos.Assunto IN ({placeholders})
            AND Topicos.Topico IN ({placeholders_1});
        """
        # Adiciona a matéria e os assuntos à tupla de parâmetros
        params = (materia,) + tuple(assuntos) + tuple(topicos)

        # Executa a consulta
        cursor.execute(query, params)

        quantidade_maxima = cursor.fetchone()[0]
        return quantidade_maxima

    except Exception as e:
        st.error(f"Erro ao obter quantidade máxima de questões: {e}")

    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

# Função para obter todas as questões
@st.cache_data
def obter_todas_questoes(materia, assuntos, topicos, quantidade):
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Monta a string de placeholders para os assuntos
        placeholders = ', '.join(['%s'] * len(assuntos))
        placeholders_1 = ', '.join(['%s'] * len(topicos))
        # Consulta para recuperar todas as questões com assuntos
        query = f"""
            SELECT
                Q.QuestaoID,
                Q.Enunciado,
                Q.Questao,
                Q.Gabarito_Oficial,
                Q.Comentario,
                M.Materia,
                A.Assunto,
                T.Topico,
                O.Orgao,
                C.Cargo,
                P.Prova, 
                Ano.Ano,   
                B.Banca                 
            FROM Questoes Q
            JOIN Materias M ON Q.MateriaID = M.MateriaID 
            JOIN Assuntos A ON Q.AssuntoID = A.AssuntoID
            JOIN Topicos T ON Q.TopicoID = T.TopicoID
            JOIN Orgaos O ON Q.OrgaoID = O.OrgaoID
            JOIN Cargos C ON Q.CargoID = C.CargoID
            JOIN Provas P ON Q.ProvaID = P.ProvaID
            JOIN Anos Ano ON Q.AnoID = Ano.AnoID
            JOIN Bancas B ON Q.BancaID = B.BancaID         
            WHERE M.Materia = %s AND A.Assunto IN ({placeholders})
            AND T.Topico IN ({placeholders_1});
        """

        # Adiciona a matéria e os assuntos à tupla de parâmetros
        params = (materia,) + tuple(assuntos) + tuple(topicos)

        # Executa a consulta
        cursor.execute(query, params)

        # Recuperar os resultados
        questoes = cursor.fetchall()

        # Embaralha as questões
        random.shuffle(questoes)

        # Limita a quantidade de questões
        questoes = questoes[:quantidade]

        return questoes

    except Exception as e:
        st.error(f"Erro ao obter questões: {e}")

    finally:
        if cnx.is_connected():
            cursor.close()
            cnx.close()

# Função principal do dashboard
def main():
    st.set_page_config(page_title="Revisão de Questões", page_icon=":pencil:")
    
    # esconde o menu
    hide_streamlit_style = """
                <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                </style>
                """

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """,
    unsafe_allow_html=True
    )
    # Inicializar variáveis de estado
    if "acertos" not in st.session_state:
        st.session_state.acertos = 0

    if "erros" not in st.session_state:
        st.session_state.erros = 0
    # Ajustar o layout e estilo da resposta 
    st.markdown(
        """
        <style>
            body {
                font-size: 16px;
            }
            .btn-primary {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 8px;
            }
            .alternativas {
                margin-bottom: 20px;
            }
            .resposta-mensagem {
                font-size: 18px;
                margin-top: 8px;
                padding: 5px;
                border-radius: 8px;
            }
            .resposta-correta {
                background-color: #5cb85c;
                color: white;
            }
            .resposta-incorreta {
                background-color: #d9534f;
                color: white;
            }
            .acertos-mensagem {
                font-size: 18px;
                margin-top: 22px;
                padding: 6px;
                border-radius: 3px;
                text-align: center;
                margin: 4px 6px;
                cursor: pointer;
                border-radius: 8px;
                display: inline-block;
            }
            .acertos-correta {
                background-color: #5cb85c;
                color: white;
            }
            .acertos-incorreta {
                background-color: #d9534f;
                color: white;
            }
        </style>
        """
        , unsafe_allow_html=True)
    #pega as informações na url# Filtro de assunto na URL
    params = st.experimental_get_query_params()
    materia = params.get("materia", ["Direito Administrativo"])[0]
    #assunto = params.get("assunto", ["Mérito Administrativo"])[0]

    # Obter a lista de assuntos disponíveis
    assuntos_disponiveis = obter_assuntos_disponiveis(materia)
    topicos_disponiveis = obter_topicos_disponiveis(materia)

    # Use st.session_state para armazenar o estado do assunto anterior
    if "assunto_filtrado_anterior" not in st.session_state:
        st.session_state.assunto_filtrado_anterior = []
    # Use st.session_state para armazenar o estado do assunto anterior
    if "topico_filtrado_anterior" not in st.session_state:
        st.session_state.topico_filtrado_anterior = []
    
    st.header(f"Questões de Revisão", divider='orange')

    with st.expander("Opções de Filtro"):
        st.info(
        "Você pode selecionar um assunto ou topico específico ou deixar vazio para ver todas as questões."
        )
        # Adicionar um seletor para o filtro de assunto
        assunto_filtrado = st.multiselect("Selecione o assunto (ou deixe vazio para todos)", assuntos_disponiveis, help='Se nenhum assunto for selecionado, serão exibidas questões de todos os assuntos.')
        
        # Adicionar um seletor para o filtro de assunto
        topico_filtrado = st.multiselect("Selecione o tópico (ou deixe vazio para todos)", topicos_disponiveis, help='Se nenhum assunto for selecionado, serão exibidas questões de todos os tópicos.')

        # Adicione um aviso informativo sobre a seleção de todos os assuntos
    
        if not assunto_filtrado:
            assunto_filtrado = assuntos_disponiveis
        if not topico_filtrado:
            topico_filtrado = topicos_disponiveis
        # Obter a quantidade máxima de questões com base no assunto filtrado

        quantidade_maxima = obter_quantidade_maxima_questoes(materia,assunto_filtrado,topico_filtrado)

        # Adicionar uma slidebar para a quantidade de questões desejada
        quantidade_questoes = st.slider("Selecione a quantidade de questões:", 2, quantidade_maxima, 10)
    
    # Antes do loop principal
    if st.session_state.get("questoes_ids") is None:
        st.session_state.questoes_ids = {}  # Inicializa o dicionário para armazenar IDs de questões

    # Reiniciar acertos e erros quando os filtros são alterados e o número da questão
    if st.session_state.get("assunto_filtrado_anterior") != assunto_filtrado or st.session_state.get("topico_filtrado_anterior") != topico_filtrado or st.session_state.get("quantidade_questoes_anterior") != quantidade_questoes:
        st.session_state.acertos = 0
        st.session_state.erros = 0
        st.session_state.questao_index=0
        st.cache_data.clear()

    # Atualizar o filtro anterior na sessão
    st.session_state.assunto_filtrado_anterior = assunto_filtrado
    st.session_state.topico_filtrado_anterior = topico_filtrado
    st.session_state.quantidade_questoes_anterior = quantidade_questoes
    # Exibir todas as questões cadastradas

    questoes = obter_todas_questoes(materia, assunto_filtrado, topico_filtrado, quantidade_questoes)
    
    # Verificar se há questões para exibir
    if questoes is None or len(questoes) == 0:
        st.warning("Não há questões disponíveis com os filtros selecionados.")
        return  # Retorna da função para evitar erros adicionais
    
    "---"        
    # Controlar o índice da questão
    questao_index = st.session_state.get("questao_index", 0)
    resposta_usuario = st.session_state.get("resposta_usuario", None)
    total_questoes = len(questoes)
    boletim = False
    col1, col2, col3 = st.columns(3)
    if questao_index == total_questoes - 1:
        with col2:
            boletim = st.button("Ver Boletim", key="ver_boletim")
    else:
    # Botões para navegar entre as questões
        with col1:
            if st.button("Questão Anterior", key='anterior_button') and questao_index > 0:
                st.markdown(
                        """
                        <script>
                            document.querySelector('[data-testid="anterior_button"]').onclick = function() {
                                // Recarrega a página quando o botão de reiniciar é clicado
                                window.location.reload();
                            };
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                questao_index -= 1
                st.session_state.questao_index = questao_index

        with col2:
            st.markdown(f"""
                <div class="acertos-mensagem acertos-correta"><strong></strong>Acertos: {st.session_state.acertos}</div>    
                <div class="acertos-mensagem acertos-incorreta"><strong>Erros:</strong> {st.session_state.erros}</div> 
            """, 
            unsafe_allow_html=True,
            )


        with col3:
            if st.button("Próxima Questão", key='proxima_button') and questao_index < total_questoes - 1:
                questao_index += 1
                st.session_state.questao_index = questao_index
                st.markdown(
                        """
                        <script>
                            document.querySelector('[data-testid="proxima_button"]').onclick = function() {
                                // Recarrega a página quando o botão de reiniciar é clicado
                                window.location.reload();
                            };
                        </script>
                        """,
                        unsafe_allow_html=True
                    )

    # cria o boletim de desempenho
    if questao_index == total_questoes - 1 and boletim:
        st.markdown(
            f"""
                <h4>Boletim de Desempenho</h4>""", 
            unsafe_allow_html=True,
            )
        # Lógica para calcular a porcentagem de acertos
        total_perguntas = total_questoes
        percentual_acertos = (st.session_state.acertos / total_perguntas) * 100

        st.write(f"**Total de Acertos:** {st.session_state.acertos}")
        st.write(f"**Total de Erros:** {st.session_state.erros}")

        if percentual_acertos >= 70:
            st.success(f"Você teve um desempenho de {percentual_acertos:.2f}% - Parabéns!")
        else:
            st.error(f"Você teve um desempenho de {percentual_acertos:.2f}% - Estude mais para melhorar!")

        # Adiciona um botão para reiniciar as questões
        reset_button_clicked = st.button("Reiniciar Questões", key="reset_button")
        
        # Adiciona código JavaScript para manipular o evento de clique do botão de reiniciar
        st.markdown(
            """
            <script>
                document.querySelector('[data-testid="reset_button"]').onclick = function() {
                    // Recarrega a página quando o botão de reiniciar é clicado
                    window.location.reload();
                };
            </script>
            """,
            unsafe_allow_html=True
        )
        #if reset_button_clicked:
        st.session_state.clear()
        # Reseta o estado da sessão
        st.session_state.questao_index = 0
        st.session_state.acertos = 0
        st.session_state.erros = 0
        st.session_state.form_questao = False
        st.session_state.expander_id = None  # Adicione esta linha para redefinir o expander_id
        st.cache_data.clear()

        # Adiciona um botão falso que aciona a recarga da página via JavaScript
        st.markdown(
            """
            <button style="display: none;" id="reloadButton" onclick="location.reload();">Reiniciar</button>
            <script>
                setTimeout(function(){
                    document.getElementById('reloadButton').click();
                }, 100);
            </script>
            """,
            unsafe_allow_html=True
        )


    else:
        
        # Selecionar a questão atual
        questao_id, enunciado, questao, gabarito_oficial, Comentario, materia, assunto, topico, orgao, cargo, prova, ano, banca = questoes[questao_index]

        st.markdown("""
            <style>
            /*
            Oculta os elementos com a classe .mostrar
            Oculta os elementos com a classe .hide-action
            */

            #box-1 .mostrar,
            #box-1 .hide-action,
            #box-2 .mostrar,
            #box-2 .hide-action {
                display: none;
            }

            /*
            conforme a HASH atual:
            Mostra os elementos com a classe .mostrar
            Mostra os elementos com a classe .hide-action
            */

            #box-1:target .mostrar,
            #box-1:target .hide-action,
            #box-2:target .mostrar,
            #box-2:target .hide-action {
                display: block;
            }

            /*
            conforme a HASH atual:
            Oculta os elementos com a classe .action-action
            */
            #box-1:target .show-action,
            #box-2:target .show-action
            {
                display: none;
            }
            </style>
                            """
        , unsafe_allow_html=True)

        with st.form("form_questao"):
            orgao_1 = orgao.split('-')[0].strip()
            st.markdown(
            f"""
            <div id="box-1">
            <div class="foo" style="display: flex; justify-content: space-between; align-items: baseline;">
                <div class="bar">
                    <div style="display: flex; align-items: baseline;">
                        <h5>Questão {questao_index + 1}/{total_questoes} - CEBRASPE (CESPE) - {orgao_1}/{ano}</h5>
                        <a href="#box-1" style="text-decoration: none; color: #007BFF; display: flex; align-items: center;margin-left: 80px;">
                            <span style="flex: 1; text-align: right; margin-right: 5px;">Mostrar Detalhes</span>
                            <i class="fas fa-info-circle" style="color: #007BFF;"></i>
                        </a>
                    </div>
                    <div class="mostrar" style="margin-top: 10px; border: 1px solid #ccc; padding: 10px; margin: 10px; border-radius: 5px;"">
                        <p><strong>Matéria:</strong> {materia}</p>
                        <p><strong>Assunto:</strong> {assunto}</p>
                        <p><strong>Tópico:</strong> {topico}</p>
                        <p><strong>Órgão:</strong> {orgao}</p>
                        <p><strong>Cargo:</strong> {cargo}</p>
                        <p><strong>Prova:</strong> {prova}</p>
                        <p><strong>Ano:</strong> {ano}</p>
                        <p><strong>Banca:</strong> {banca}</p> 
                    </div>              
                </div>
            </div>
            <div class="baz">
                <a class="hide-action" href="#" style="margin-top: 10px; background-color: #DC3545; color: #fff; padding: 6px; border-radius: 5px;margin-left: 540px; margin-right: 45px;">
                    <i class="fas fa-times" style="margin-right: 5px; margin-left: 5px;"></i>Fechar
                </a>
            </div>
            </div>
            <div style="padding: 15px; margin: 5px 0; border-radius: 5px;" >
                <p>{enunciado}</p>
                <p>{questao}</p>
            </div>
            """, 
            unsafe_allow_html=True,
            )

            # Radio button para escolher a resposta
            resposta_usuario = st.radio(
                "",
                options=["Certo", "Errado"],
                key=f"resposta_radio_{questao_index}",
                help="",
                format_func=lambda x: f"**{x}**",
                index=None
            )
            
            # Adicionando o HTML personalizado com o botão de comentário
            # Adicionando o HTML personalizado com os botões alinhados
            col1, col2 = st.columns(2)
            #resposta_usuario = st.radio("", ["Certo", "Errado"], key=f"resposta_radio_{questao_index}", index=None)
            if col1.form_submit_button("Confirmar Resposta"):
                if resposta_usuario:
                    mensagem = ""
                    if resposta_usuario == gabarito_oficial:
                        mensagem = '<p><div class="resposta-mensagem resposta-correta">Parabéns! Sua resposta está correta.</div></p>'
                        st.session_state.acertos += 1
                    else:
                        mensagem = f'<p><div class="resposta-mensagem resposta-incorreta">Você errou! Gabarito: <strong>{gabarito_oficial}</strong></div></p>'
                        st.session_state.erros += 1
                    # Salvar as respostas do aluno
                    salvar_respostas_aluno(questao_id, resposta_usuario, gabarito_oficial, assunto, topico)

                else:
                    mensagem = 'Favor selecionar uma resposta'
                st.markdown(mensagem, unsafe_allow_html=True)

            # Botão de mostrar comentário na coluna 2
            if col2.markdown(f"""
                <div id="box-3">
                    <div class="foo" style="display: flex; justify-content: space-between; align-items: baseline;">
                        <div class="bar">
                            <div style="display: flex; align-items: baseline;">
                                <a href="#box-2" style="text-decoration: none; color: #007BFF; display: flex; align-items: center;margin-left: 150px;">
                                    <span style="flex: 1; text-align: right; margin-right: 5px;">Comentário</span>
                                    <i class="fas fa-comment" style="margin-right: 5px; margin-left: 5px;"></i>
                                </a>
                            </div>             
                        </div>
                    </div>
                    </div>
                    """, 
                    unsafe_allow_html=True,
                    
            ):
                pass
            st.markdown(
                f"""
                <div id="box-2">
                    <div class="foo" style="display: flex; justify-content: space-between; align-items: baseline;">
                        <div class="bar">
                            <div style="display: flex; align-items: baseline;">
                            </div>
                            <div class="mostrar" style="margin-top: 6px; border: 1px solid #ccc; padding: 10px; margin: 6px; border-radius: 5px;"">
                                <p><strong>Comentário:</strong> {Comentario}</p>
                            </div>              
                        </div>
                    </div>
                    <div class="baz">
                        <a class="hide-action" href="#" style="margin-top: 10px; background-color: #DC3545; color: #fff; padding: 6px; border-radius: 5px;margin-left: 540px; margin-right: 45px;">
                            <i class="fas fa-times" style="margin-right: 5px; margin-left: 5px;"></i>Fechar 
                        </a>
                        <p></p>
                    </div>
                    </div>
                    """, 
                    unsafe_allow_html=True,
                    )

        # Adicionando um espaço para a mensagem de JavaScript
        st.markdown(
            """
            <script>
                // Esconde o comentário ao mudar de questão
                document.addEventListener('sessionStateChanged', function(event) {
                    // Desmarca o radio button ao mudar de questão
                    document.querySelectorAll('input[name^="resposta_usuario"]').forEach(function(radio) {
                        radio.checked = false;
                    });

                // Desmarca o radio button ao carregar a página
                document.addEventListener('DOMContentLoaded', function() {
                    document.querySelectorAll('input[name^="resposta_usuario"]').forEach(function(radio) {
                        radio.checked = false;
                    });
                });
            </script>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <script>
                // Fecha o expander ao mudar de questão
                document.addEventListener('sessionStateChanged', function(event) {
                    var expander = document.querySelector('st.expander > .stDecoratedContent');
                    if (expander) {
                        expander.style.display = 'none';
                    }
                });
            </script>
            """,
            unsafe_allow_html=True
        )      

if __name__ == "__main__":
    main()
