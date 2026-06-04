CREATE OR REPLACE PROCEDURE sp_movimentacao_filtro(
    p_produto VARCHAR,
    p_fornecedor VARCHAR,
    p_cursor REFCURSOR
)
LANGUAGE plpgsql
AS
$$
DECLARE
    v_sql TEXT;
BEGIN

    v_sql := '
        SELECT

            dp.id_produto,
            dp.descricao_prod,
            dp.categoria_prod,
            dp.procedencia_prod,

            df.nome_forn,

            dt.nome_transp,

            dl.numero_lote,
            dl.data_validade_lote,

            tm.descricao_mov,

            fm.quantidade,
            fm.valor_total,
            fm.data

        FROM fato_movimentacao fm

        LEFT JOIN dim_produto dp
            ON fm.id_produto = dp.id_produto

        LEFT JOIN dim_fornecedor df
            ON fm.id_fornecedor = df.id_fornecedor

        LEFT JOIN dim_transportadora dt
            ON fm.id_transp = dt.id_transp

        LEFT JOIN dim_lote dl
            ON fm.id_lote = dl.id_lote

        LEFT JOIN dim_tipo_mov tm
            ON fm.id_tipo_mov = tm.id_tipo_mov

        WHERE 1=1
    ';

    IF p_produto IS NOT NULL
       AND p_produto <> '' THEN

        v_sql := v_sql ||
        format(
            ' AND LOWER(dp.descricao_prod) LIKE LOWER(%L)',
            '%' || p_produto || '%'
        );

    END IF;

    IF p_fornecedor IS NOT NULL
       AND p_fornecedor <> '' THEN

        v_sql := v_sql ||
        format(
            ' AND LOWER(df.nome_forn) LIKE LOWER(%L)',
            '%' || p_fornecedor || '%'
        );

    END IF;

    v_sql := v_sql || '
        ORDER BY fm.data DESC
    ';

    RAISE NOTICE 'SQL: %', v_sql;

    OPEN p_cursor FOR EXECUTE v_sql;

END;
$$;

BEGIN;

CALL sp_movimentacao_filtro(
    '',
    '',
    'cursor_mov'
);

FETCH ALL FROM cursor_mov;

COMMIT;
