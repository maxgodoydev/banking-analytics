-- Esquema do banco de dados SINTÉTICO usado neste projeto.
-- Nenhum dado aqui representa pessoas, empresas ou transações reais.

CREATE TABLE clientes (
    cliente_id    INTEGER PRIMARY KEY,
    segmento      TEXT NOT NULL CHECK (segmento IN ('Varejo', 'Premium', 'Pequena Empresa')),
    uf            TEXT NOT NULL,
    data_cadastro TEXT NOT NULL            -- formato AAAA-MM-DD
);

CREATE TABLE contas (
    conta_id    INTEGER PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES clientes (cliente_id),
    tipo_conta  TEXT NOT NULL CHECK (tipo_conta IN ('corrente', 'poupanca'))
);

CREATE TABLE transacoes (
    transacao_id INTEGER PRIMARY KEY,
    conta_id     INTEGER NOT NULL REFERENCES contas (conta_id),
    data_hora    TEXT NOT NULL,            -- formato AAAA-MM-DD HH:MM:SS
    tipo         TEXT NOT NULL CHECK (tipo IN ('PIX', 'TED', 'Boleto', 'Debito', 'Credito')),
    canal        TEXT NOT NULL,
    valor        REAL NOT NULL CHECK (valor > 0),   -- REAL por simplicidade (ver README)
    status       TEXT NOT NULL CHECK (status IN ('concluida', 'negada'))
);

CREATE INDEX idx_transacoes_conta ON transacoes (conta_id);
CREATE INDEX idx_transacoes_data  ON transacoes (data_hora);
