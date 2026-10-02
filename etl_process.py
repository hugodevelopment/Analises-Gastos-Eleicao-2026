import os
import pandas as pd

def clean_doc(doc):
    """Higieniza CPFs e CNPJs: remove marcadores nulos do TSE e completa zeros à esquerda."""
    if pd.isna(doc):
        return None
    doc_str = str(doc).strip()
    if doc_str in ['#NULO#', '#NULO', '-1', '-3', 'nan', 'None', '']:
        return None
    
    # Mantém apenas dígitos numéricos
    digits = ''.join(c for c in doc_str if c.isdigit())
    if len(digits) == 0:
        return None
    if len(digits) <= 11:
        return digits.zfill(11)  # CPF
    elif len(digits) <= 14:
        return digits.zfill(14)  # CNPJ
    return digits


def clean_text(text):
    """Padroniza textos em caixa alta e substitui marcadores de erro do TSE."""
    if pd.isna(text):
        return 'NÃO INFORMADO'
    text_str = str(text).strip().upper()
    if text_str in ['#NULO#', '#NULO', '-1', '-3']:
        return 'NÃO INFORMADO'
    return text_str


def process_receitas(input_path, output_path):
    """Lê, sanitiza, padroniza e salva a base de Receitas."""
    print(f"\n[1/2] Iniciando ETL de RECEITAS: {input_path}")
    if not os.path.exists(input_path):
        print(f"  [ERRO] Arquivo não encontrado: {input_path}")
        return None
        
    df = pd.read_csv(input_path, sep=';', encoding='latin1', low_memory=False)
    
    # 1. Conversão Monetária
    df['vr_receita'] = df['VR_RECEITA'].astype(str).str.replace(',', '.').astype(float)
    
    # 2. Conversão de Datas
    df['dt_receita'] = pd.to_datetime(df['DT_RECEITA'], format='%d/%m/%Y', errors='coerce')
    
    # 3. Tratamento de Documentos (CPF/CNPJ)
    df['nr_cpf_cnpj_doador'] = df['NR_CPF_CNPJ_DOADOR'].apply(clean_doc)
    
    # 4. Dados do Candidato
    df['id_candidato'] = df['SQ_CANDIDATO'].astype(str)
    df['nm_candidato'] = df['NM_CANDIDATO'].apply(clean_text)
    df['ds_cargo'] = df['DS_CARGO'].apply(clean_text)
    df['sg_partido'] = df['SG_PARTIDO'].apply(clean_text)
    df['ds_genero'] = df['DS_GENERO'].apply(clean_text)
    df['ds_cor_raca'] = df['DS_COR_RACA'].apply(clean_text)
    
    # 5. Dados do Doador
    df['nm_doador'] = df['NM_DOADOR'].apply(clean_text)
    
    # 6. Categorias Financeiras
    df['ds_fonte_receita'] = df['DS_FONTE_RECEITA'].apply(clean_text)
    df['ds_origem_receita'] = df['DS_ORIGEM_RECEITA'].apply(clean_text)
    df['ds_especie_receita'] = df['DS_ESPECIE_RECEITA'].apply(clean_text)
    df['ds_natureza_receita'] = df['DS_NATUREZA_RECEITA'].apply(clean_text)
    
    # 7. Identificador Único
    df['id_receita'] = df['SQ_RECEITA'].astype(str)
    
    cols = [
        'id_receita', 'id_candidato', 'nm_candidato', 'ds_cargo', 'sg_partido',
        'ds_genero', 'ds_cor_raca', 'dt_receita', 'vr_receita',
        'nr_cpf_cnpj_doador', 'nm_doador', 'ds_fonte_receita', 
        'ds_origem_receita', 'ds_especie_receita', 'ds_natureza_receita'
    ]
    
    df_clean = df[cols].copy()
    
    # Salvar em CSV
    df_clean.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
    print(f"  [SUCESSO] Receitas salvas em: {output_path}")
    print(f"  [METRICAS] {len(df_clean):,} registros | Total: R$ {df_clean['vr_receita'].sum():,.2f}")
    
    return df_clean


def process_despesas(input_path, output_path):
    """Lê, sanitiza, padroniza e salva a base de Despesas."""
    print(f"\n[2/2] Iniciando ETL de DESPESAS: {input_path}")
    if not os.path.exists(input_path):
        print(f"  [AVISO] Arquivo de despesas ainda não encontrado em: {input_path}")
        print("  Coloque o arquivo 'despesas_candidatos_2022_RJ.csv' na pasta 'data/raw/' para processá-lo.")
        return None
        
    df = pd.read_csv(input_path, sep=';', encoding='latin1', low_memory=False)
    
    # 1. Conversão Monetária (Pode ser VR_DESPESA_CONTRATADA ou VR_PAGO dependendo do arquivo TSE)
    valor_col = 'VR_DESPESA_CONTRATADA' if 'VR_DESPESA_CONTRATADA' in df.columns else 'VR_PAGO'
    df['vr_despesa'] = df[valor_col].astype(str).str.replace(',', '.').astype(float)
    
    # 2. Conversão de Datas
    df['dt_despesa'] = pd.to_datetime(df['DT_DESPESA'], format='%d/%m/%Y', errors='coerce')
    
    # 3. Tratamento de Documentos (CPF/CNPJ Fornecedor)
    df['nr_cpf_cnpj_fornecedor'] = df['NR_CPF_CNPJ_FORNECEDOR'].apply(clean_doc)
    
    # 4. Dados do Candidato
    df['id_candidato'] = df['SQ_CANDIDATO'].astype(str)
    df['nm_candidato'] = df['NM_CANDIDATO'].apply(clean_text)
    df['ds_cargo'] = df['DS_CARGO'].apply(clean_text)
    df['sg_partido'] = df['SG_PARTIDO'].apply(clean_text)
    
    # 5. Dados do Fornecedor e Tipo de Gasto
    df['nm_fornecedor'] = df['NM_FORNECEDOR'].apply(clean_text)
    df['ds_origem_despesa'] = df['DS_ORIGEM_DESPESA'].apply(clean_text) if 'DS_ORIGEM_DESPESA' in df.columns else 'NÃO INFORMADO'
    df['ds_despesa'] = df['DS_DESPESA'].apply(clean_text) if 'DS_DESPESA' in df.columns else 'NÃO INFORMADO'
    
    # 6. Identificador Único
    df['id_despesa'] = df['SQ_DESPESA'].astype(str) if 'SQ_DESPESA' in df.columns else df.index.astype(str)
    
    cols = [
        'id_despesa', 'id_candidato', 'nm_candidato', 'ds_cargo', 'sg_partido',
        'dt_despesa', 'vr_despesa', 'nr_cpf_cnpj_fornecedor', 'nm_fornecedor',
        'ds_origem_despesa', 'ds_despesa'
    ]
    
    df_clean = df[cols].copy()
    
    # Salvar em CSV
    df_clean.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
    print(f"  [SUCESSO] Despesas salvas em: {output_path}")
    print(f"  [METRICAS] {len(df_clean):,} registros | Total: R$ {df_clean['vr_despesa'].sum():,.2f}")
    
    return df_clean


if __name__ == '__main__':
    # Garante a criação do diretório de destino
    os.makedirs('data/processed', exist_ok=True)
    
    # Mapeamento de Arquivos
    path_raw_rec = 'data/raw/receitas_candidatos_2026_RJ.csv'
    path_out_rec = 'data/processed/receitas_clean.csv'
    
    path_raw_desp = 'data/raw/despesas_contratadas_candidatos_2026_RJ.csv'
    path_out_desp = 'data/processed/despesas_clean.csv'
    
    # Executa ambas as etapas de processamento
    process_receitas(input_path=path_raw_rec, output_path=path_out_rec)
    process_despesas(input_path=path_raw_desp, output_path=path_out_desp)