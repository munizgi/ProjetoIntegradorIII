

from flask import Flask, render_template, request, jsonify  # importa flask e funções usadas nas rotas e respostas
from sqlalchemy import create_engine, text  # importa conexão sql e textos sql parametrizados
import pandas as pd  # importa pandas para transformar resultados em dataframe
from prophet import Prophet  # importa prophet para previsão temporal na área de ia

app = Flask(__name__)

# =========================================================
# conexão
# =========================================================

engine = create_engine(  # cria o motor de conexão com o postgresql
    "postgresql+psycopg2://postgres:753614@localhost:5432/relacionalMFIX"
)

# =========================================================
# query padrão
# =========================================================

def query_db(query, params={}):  # cria função padrão para executar selects e devolver lista de dicionários

    with engine.connect() as conn:  # abre conexão temporária com o banco

        result = conn.execute(  # executa a consulta sql usando parâmetros seguros
            text(query),  # converte a string sql para objeto executável pelo sqlalchemy
            params  # envia os parâmetros usados nos filtros
        )

        df = pd.DataFrame(  # monta um dataframe com as linhas retornadas
            result.fetchall(),  # pega todas as linhas retornadas pelo banco
            columns=result.keys()  # usa os nomes das colunas vindos da consulta
        )

    return df.to_dict(orient="records")  # converte o dataframe para lista de dicionários usada pelo html

# =========================================================
# interface dw
# =========================================================

@app.route("/", methods=["GET", "POST"]) 
def home():  # controla a tela inicial com filtros e kpis

    produto = request.form.get( 
        "produto", ""  
    ).strip()  

    fornecedor = request.form.get( 
        "fornecedor", "" 
    ).strip()  

    movimentacao = request.form.get( 
        "movimentacao", ""  
    ).strip()  

    data_inicial = request.form.get(  
        "data_inicial", ""  
    ).strip()  

    data_final = request.form.get(  
        "data_final", ""  
    ).strip()  

    query = """

        SELECT

            dp.descricao_prod,
            dp.categoria_prod,
            dp.procedencia_prod,

            COALESCE(df.nome_forn, 'Não informado')
            AS nome_forn,

            tm.descricao_mov,

            COALESCE(dt.nome_transp, 'Não informado')
            AS nome_transp,

            dl.numero_lote,
            dl.data_validade_lote,

            fm.quantidade,
            fm.valor_total,

            TO_CHAR(
                fm.data,
                'DD/MM/YYYY'
            ) AS data,

            (

                SELECT MAX(f2.quantidade)

                FROM fato_movimentacao f2

                WHERE
                    f2.id_produto = fm.id_produto
                    AND f2.id_tipo_mov = 2

            ) AS melhor_venda

        FROM fato_movimentacao fm

        LEFT JOIN dim_produto dp
        ON fm.id_produto = dp.id_produto

        LEFT JOIN dim_fornecedor df
        ON fm.id_fornecedor = df.id_fornecedor

        LEFT JOIN dim_tipo_mov tm
        ON fm.id_tipo_mov = tm.id_tipo_mov

        LEFT JOIN dim_transportadora dt
        ON fm.id_transp = dt.id_transp

        LEFT JOIN dim_lote dl
        ON fm.id_lote = dl.id_lote

        WHERE 1=1

    """

    params = {}

    # =====================================================
    # movimentação
    # =====================================================

    if movimentacao != "":  # verifica se o usuário selecionou uma movimentação

        query += """

            AND CAST(fm.id_tipo_mov AS TEXT)
            = :movimentacao

        """

        params["movimentacao"] = str(movimentacao)

   # =====================================================
    # data inicial
    # =====================================================

    if data_inicial != "":  # verifica se o usuário informou data inicial

        query += """

            AND fm.data <= CAST(:data_final AS DATE)

        """

        params["data_inicial"] = data_inicial

    # =====================================================
    # data final
    # =====================================================

    if data_final != "":  # verifica se o usuário informou data final

        query += """

            AND fm.data <= :data_final

        """

        params["data_final"] = data_final

    query += """

        ORDER BY fm.data DESC

        LIMIT 200

    """

    dados = query_db(query, params)  # consulta dados que serão exibidos no modal
    
    # =====================================================
    # kpis home
    # =====================================================
    # consulta indicadores rápidos da tela inicial
    kpis = query_db("""  

        SELECT

            COUNT(*) AS total_mov,

            COUNT(DISTINCT id_fornecedor)
            AS fornecedores,

            COUNT(*) FILTER(
        WHERE id_tipo_mov = 2
        AND data = CURRENT_DATE
    ) AS movimentacoes_hoje

        FROM fato_movimentacao

    """)

    return render_template(  # renderiza a página html com os dados calculados
        "index.html",  # informa qual template será exibido
        dados=dados,  # manda os registros da tabela para o html
        kpis=kpis  # manda os indicadores para o html
    )

# =========================================================
# autocomplete
# =========================================================

@app.route("/autocomplete_produto")  # define rota usada pelo autocomplete de produto
def autocomplete_produto():  # busca sugestões de produtos conforme o usuário digita

    termo = request.args.get("term", "")  # pega o termo digitado na busca do autocomplete
    # consulta produtos parecidos com o termo digitado
    produtos = query_db("""  

        SELECT DISTINCT descricao_prod

        FROM dim_produto

        WHERE LOWER(descricao_prod)
        LIKE LOWER(:termo)

        ORDER BY descricao_prod

        LIMIT 10

    """, {

        "termo": f"%{termo}%"

    })

    return jsonify(produtos)  # devolve as sugestões em json para o frontend

# =========================================================
# dashboard
# =========================================================

@app.route("/dashboard")  # define a rota do dashboard gerencial
def dashboard():  # monta os indicadores e gráficos do dashboard

    # ==========================================
    # kpis principais
    # ==========================================
    
    kpis = query_db("""  

    SELECT

            COUNT(*) AS total_mov,

            ROUND(
                SUM(valor_total)
                FILTER(
                    WHERE id_tipo_mov = 2
                )::numeric,
                2
            ) AS receita,

            COUNT(DISTINCT id_produto)
            AS produtos

    FROM fato_movimentacao

    WHERE data >= CURRENT_DATE - INTERVAL '2 years'

""")
    # ==========================================
    # fornecedores
    # ==========================================

    fornecedores = query_db("""  

       SELECT
            COUNT(DISTINCT id_fornecedor)
            AS fornecedores

        FROM fato_movimentacao

        WHERE data >= CURRENT_DATE - INTERVAL '2 years'

    """)

    # ==========================================
    # entradas
    # ==========================================

    entradas = query_db("""  

      SELECT
        COUNT(*) AS entradas
    FROM fato_movimentacao
    WHERE id_tipo_mov = 1
    AND data >= CURRENT_DATE - INTERVAL '2 years'

    """)

    # ==========================================
    # saídas
    # ==========================================

    saidas = query_db("""  

       SELECT
        COUNT(*) AS saidas
    FROM fato_movimentacao
    WHERE id_tipo_mov = 2
    AND data >= CURRENT_DATE - INTERVAL '2 years'
                      
    """)

 # ==========================================
# ticket médio
# ==========================================

    ticket_medio = query_db("""

    SELECT

        ROUND(
            AVG(valor_total)::numeric,
            2
        ) AS ticket

    FROM fato_movimentacao

    WHERE id_tipo_mov = 2
    AND data >= CURRENT_DATE - INTERVAL '2 years'

    """)
    # ==========================================
    # categorias
    # ==========================================

    categorias = query_db(""" 

    SELECT

        dp.categoria_prod,
        ROUND(
            SUM(fm.valor_total)::numeric,
            2
        ) AS total

    FROM fato_movimentacao fm

    JOIN dim_produto dp
        ON fm.id_produto = dp.id_produto

    WHERE fm.data >= CURRENT_DATE - INTERVAL '2 years'
    AND fm.id_tipo_mov = 2

    GROUP BY dp.categoria_prod

    ORDER BY total DESC

    """)
    # ==========================================
    # ajustes
    # ==========================================

    ajustes = query_db("""  

        SELECT
        COUNT(*) AS ajustes
    FROM fato_movimentacao
    WHERE id_tipo_mov = 3
    AND data >= CURRENT_DATE - INTERVAL '2 years'

    """)

    # ==========================================
    # top produtos
    # ==========================================
    # busca os cinco produtos mais vendidos em quantidade
    top_produtos = query_db("""  

        SELECT

            p.descricao_prod,

            SUM(fm.quantidade)
            AS total

        FROM fato_movimentacao fm

        JOIN dim_produto p
        ON fm.id_produto = p.id_produto

        WHERE fm.id_tipo_mov = 2
          AND fm.data >= CURRENT_DATE - INTERVAL '2 years'

        GROUP BY p.descricao_prod

        ORDER BY total DESC

        LIMIT 5

    """)

    # ==========================================
    # financeiro
    # ==========================================
     # calcula evolução mensal do faturamento
    financeiro = query_db(""" 

       SELECT
            TO_CHAR(data, 'MM/YYYY') AS data,

            ROUND(
                SUM(valor_total)::numeric,
                2
            ) AS total

        FROM fato_movimentacao

        WHERE id_tipo_mov = 2
          AND data >= CURRENT_DATE - INTERVAL '2 years'

        GROUP BY TO_CHAR(data, 'MM/YYYY'),
                DATE_TRUNC('month', data)

        ORDER BY DATE_TRUNC('month', data);
                          
    """)

    # ==========================================
    # crescimento
    # ==========================================
    # calcula crescimento percentual entre janeiro e dezembro
    crescimento = query_db("""  

         SELECT
    ROUND(
        (
            SUM(
                CASE
                    WHEN EXTRACT(MONTH FROM data) = 12
                    THEN valor_total
                    ELSE 0
                END
            )
            -
            SUM(
                CASE
                    WHEN EXTRACT(MONTH FROM data) = 1
                    THEN valor_total
                    ELSE 0
                END
            )
        ) * 100.0
        /
        NULLIF(
            SUM(
                CASE
                    WHEN EXTRACT(MONTH FROM data) = 1
                    THEN valor_total
                    ELSE 0
                END
            ),
            0
        ),
        2
    ) AS crescimento

FROM fato_movimentacao

WHERE id_tipo_mov = 2
AND data >= CURRENT_DATE - INTERVAL '2 years'

            """)
#------------------------------------------------------#
    return render_template(  # renderiza a página html com os dados calculados

        "dashboard.html",  # informa qual template do dashboard será exibido

        kpis=kpis,  # manda os indicadores para o html

        fornecedores=fornecedores,  # manda o indicador de fornecedores para o template

        entradas=entradas,  # manda o total de entradas para o template

        saidas=saidas,  # manda o total de saídas para o template

        ajustes=ajustes,  # manda o total de ajustes para o template

        ticket_medio=ticket_medio,  # manda o ticket médio para o template

        top_produtos=top_produtos,  # manda o ranking de produtos para o template

        financeiro=financeiro,  # manda a série mensal financeira para o template
        
        categorias=categorias,  # manda o total por categoria para o template
        
        crescimento=crescimento  # manda o percentual de crescimento para o template

    )
    # ==========================================
    # ia
    # ==========================================

@app.route("/ia")  # define a rota da análise preditiva
def ia():  # executa estatística e previsão de faturamento
        # lê dados de saída direto do banco para análise
        df_ia = pd.read_sql("""  

            SELECT
                data,
                valor_total

            FROM fato_movimentacao

            WHERE id_tipo_mov = 2

        """, engine)

        df_ia["data"] = pd.to_datetime(  # converte a coluna de data para formato temporal
            df_ia["data"]
        )

        dados_diarios = (  # agrupa o faturamento por dia

            df_ia.groupby("data")["valor_total"]  # soma valor total por data
            .sum()  # soma o faturamento diário
            .reset_index()  # reorganiza o índice após o agrupamento

        )

        # com outliers

        media_preco = round(  # calcula a média com outliers
                dados_diarios["valor_total"].mean(),
                2
            )

        mediana_preco = round(  # calcula a mediana com outliers
                dados_diarios["valor_total"].median(),
                2
            )

        desvio_padrao = round(  # calcula o desvio padrão com outliers
                dados_diarios["valor_total"].std(),
                2
            )

        Q1 = dados_diarios["valor_total"].quantile(0.25)  # calcula o primeiro quartil para detectar outliers

        Q3 = dados_diarios["valor_total"].quantile(0.75)  # calcula o terceiro quartil para detectar outliers

        IQR = Q3 - Q1  # calcula a amplitude interquartil

        limite_inferior = Q1 - (1.5 * IQR)  # define limite inferior para outliers

        limite_superior = Q3 + (1.5 * IQR)  # define limite superior para outliers


        prophet_df = dados_diarios.rename(  # prepara dataframe no formato exigido pelo prophet
            columns={
                "data": "ds",
                "valor_total": "y"
            }
        )


        modelo = Prophet(  # cria o modelo de previsão temporal
            daily_seasonality=True,  # ativa sazonalidade diária
            weekly_seasonality=True,  # ativa sazonalidade semanal
            yearly_seasonality=False  # desativa sazonalidade anual
        )

        modelo.fit(prophet_df)  # treina o modelo prophet com dados históricos


        future = modelo.make_future_dataframe(  # cria datas futuras para previsão
            periods=56  # define previsão para 56 dias, equivalente a 8 semanas
        )

        forecast = modelo.predict(future)  # gera as previsões futuras

        previsao_8_semanas = forecast.tail(56)  # separa somente as próximas 8 semanas previstas

        media_futura = round(  # calcula média prevista para o futuro
            previsao_8_semanas["yhat"].mean(),
            2
        )

        maximo_previsto = round(  # calcula maior valor previsto
            previsao_8_semanas["yhat"].max(),
            2
        )

        minimo_previsto = round(  # calcula menor valor previsto
            previsao_8_semanas["yhat"].min(),
            2
        )


        if media_futura > media_preco:  # compara previsão com média histórica
            tendencia = "CRESCIMENTO"  # define a tendência textual exibida na tela
        elif media_futura < media_preco:  # verifica cenário de queda
            tendencia = "QUEDA"  # define a tendência textual exibida na tela
        else:  # trata cenário sem alta ou queda
            tendencia = "ESTÁVEL"  # define a tendência textual exibida na tela

        insight = f"""  
                A previsão para as próximas 8 semanas
                indica faturamento médio estimado de
                R$ {str(f"{media_futura:,.2f}").replace(',', 'X').replace('.', ',').replace('X', '.')}.

                O maior valor previsto é
                R$ {str(f"{maximo_previsto:,.2f}").replace(',', 'X').replace('.', ',').replace('X', '.')}.

                O menor valor previsto é
                R$ {str(f"{minimo_previsto:,.2f}").replace(',', 'X').replace('.', ',').replace('X', '.')}.

                Tendência: {tendencia}.
                """


        outliers = dados_diarios[  # filtra registros considerados outliers

            (
                dados_diarios["valor_total"]
                < limite_inferior
            )

            |

            (
                dados_diarios["valor_total"]
                > limite_superior
            )

        ]

        dados_sem_outliers = dados_diarios[  # mantém apenas dados dentro dos limites estatísticos

            (
                dados_diarios["valor_total"]
                >= limite_inferior
            )

            &

            (
                dados_diarios["valor_total"]
                <= limite_superior
            )

        ]

                # sem outliers

        media_limpa = round(  # calcula média sem outliers
            dados_sem_outliers["valor_total"].mean(),
            2
        )

        mediana_limpa = round(  # calcula mediana sem outliers
            dados_sem_outliers["valor_total"].median(),
            2
        )

        desvio_limpo = round(  # calcula desvio padrão sem outliers
            dados_sem_outliers["valor_total"].std(),
            2
        )

        return render_template(  # renderiza a página html com os dados calculados

            "ia.html",  # informa qual template da ia será exibido

            media=media_preco,  # manda a média original para o template

            mediana=mediana_preco,  # manda a mediana original para o template

            desvio=desvio_padrao,  # manda o desvio original para o template

            media_limpa=media_limpa,  # manda média sem outliers para o template
            mediana_limpa=mediana_limpa,  # manda mediana sem outliers para o template
            desvio_limpo=desvio_limpo,  # manda desvio sem outliers para o template

            qtd_outliers=len(outliers),  # manda quantidade de outliers encontrados

            dados_ia=dados_diarios.to_dict(  # manda dados originais agregados para gráficos
                orient="records"
            ),

            dados_limpos=dados_sem_outliers.to_dict(  # manda dados limpos para gráficos
                orient="records"
            ),
             previsao=previsao_8_semanas.to_dict(  # manda previsão de 8 semanas para gráficos
                orient="records"
            ),
                    
            media_futura=media_futura,  # manda média prevista para o template
            maximo_previsto=maximo_previsto,  # manda máximo previsto para o template
            minimo_previsto=minimo_previsto,  # manda mínimo previsto para o template
            tendencia=tendencia,  # manda tendência calculada para o template
            insight=insight  # manda texto interpretativo para o template

        )
# =========================================================
# modal produto
# =========================================================

@app.route("/produto/<nome>")  # define rota do modal de detalhes do produto
def produto(nome):  # busca movimentações específicas de um produto
# consulta dados que serão exibidos no modal
    dados = query_db("""  

        SELECT

            dp.descricao_prod,
            df.nome_forn,
            dl.numero_lote,
            dl.data_validade_lote,
            tm.descricao_mov,
            fm.quantidade,
            fm.valor_total,
            dt.nome_transp,
            TO_CHAR(
                fm.data,
                'DD/MM/YYYY'
            ) AS data
                     
        FROM fato_movimentacao fm

        LEFT JOIN dim_produto dp
        ON fm.id_produto = dp.id_produto

        LEFT JOIN dim_fornecedor df
        ON fm.id_fornecedor = df.id_fornecedor

        LEFT JOIN dim_lote dl
        ON fm.id_lote = dl.id_lote

        LEFT JOIN dim_tipo_mov tm
        ON fm.id_tipo_mov = tm.id_tipo_mov

        LEFT JOIN dim_transportadora dt
        ON fm.id_transp = dt.id_transp

        WHERE LOWER(dp.descricao_prod)
        = LOWER(:nome)

        ORDER BY fm.data DESC

        LIMIT 10

    """, {

        "nome": nome  # envia o nome do produto como parâmetro seguro

    })

    return jsonify(dados)  # devolve os detalhes do produto em json

# =========================================================
# procedure cursor para fazer filtros
# =========================================================

def executar_cursor_movimentacao(  # função python responsável por chamar a procedure com cursor
    produto,  # envia este filtro para a função de cursor
    fornecedor
):

    with engine.connect() as conn:  # abre conexão temporária com o banco

        trans = conn.begin()  # abre transação exigida para trabalhar com cursor

        conn.execute(text("""

            CALL sp_movimentacao_filtro(
                :produto,
                :fornecedor,
                'cursor_mov'
            )

        """), {

            "produto": produto,  # envia produto para a procedure
            "fornecedor": fornecedor  # envia fornecedor para a procedure

        })

        result = conn.execute(  # executa a consulta sql usando parâmetros seguros
            text(
                "FETCH ALL FROM cursor_mov"
            )
        )

        df = pd.DataFrame(  # monta um dataframe com as linhas retornadas
            result.fetchall(),  # pega todas as linhas retornadas pelo banco
            columns=result.keys()  # usa os nomes das colunas vindos da consulta
        )

        trans.commit()  # confirma a transação após buscar os dados

    return df.to_dict(  # converte o dataframe para lista de dicionários usada pelo html
        orient="records"
    )

# =========================================================
# start
# =========================================================

if __name__ == "__main__":  # garante que o flask rode só quando o arquivo for executado direto
    app.run(debug=True)  # inicia o servidor flask em modo debug
