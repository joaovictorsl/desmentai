"""
Sistema de ingestão de dados para o DesmentAI.
"""

import os
import requests
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngestion:
    """Classe para ingestão de dados de fontes confiáveis."""
    
    def __init__(self, data_path: str = "data/raw"):
        """
        Inicializa o sistema de ingestão.
        
        Args:
            data_path: Caminho para salvar os dados
        """
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Fontes confiáveis conhecidas
        self.trusted_sources = {
            "agencia_lupa": {
                "name": "Agência Lupa",
                "base_url": "https://piaui.folha.uol.com.br/lupa/",
                "type": "fact_checking"
            },
            "aos_fatos": {
                "name": "Aos Fatos",
                "base_url": "https://www.aosfatos.org/",
                "type": "fact_checking"
            },
            "boatos_org": {
                "name": "Boatos.org",
                "base_url": "https://www.boatos.org/",
                "type": "fact_checking"
            },
            "g1": {
                "name": "G1",
                "base_url": "https://g1.globo.com/",
                "type": "news"
            },
            "folha": {
                "name": "Folha de S.Paulo",
                "base_url": "https://www1.folha.uol.com.br/",
                "type": "news"
            }
        }
    
    def download_sample_data(self) -> bool:
        """
        Baixa dados de exemplo para demonstração.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info("Baixando dados de exemplo...")
            
            # Criar dados de exemplo
            sample_data = self._create_sample_data()
            
            # Salvar dados
            for source, data in sample_data.items():
                file_path = self.data_path / f"{source}.txt"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                logger.info(f"Dados de exemplo salvos: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao baixar dados de exemplo: {str(e)}")
            return False
    
    def _create_sample_data(self) -> Dict[str, str]:
        """Cria dados de exemplo para demonstração."""
        return {
            "agencia_lupa": """
VERIFICAÇÃO: Brasil é o maior produtor de café do mundo

VERDADEIRO. O Brasil é realmente o maior produtor de café do mundo, responsável por cerca de 1/3 da produção global. O país produz aproximadamente 60 milhões de sacas de café por ano, seguido pelo Vietnã e Colômbia.

Fonte: Agência Lupa - https://piaui.folha.uol.com.br/lupa/
Data: 2024
""",
            "aos_fatos": """
VERIFICAÇÃO: Vacinas contra COVID-19 causam autismo

FALSO. Não há evidências científicas que comprovem que vacinas contra COVID-19 causam autismo. Estudos científicos extensivos mostram que as vacinas são seguras e eficazes. A relação entre vacinas e autismo foi desmentida por múltiplas pesquisas.

Fonte: Aos Fatos - https://www.aosfatos.org/
Data: 2024
""",
            "boatos_org": """
VERIFICAÇÃO: Terra é plana

FALSO. A Terra é esférica, não plana. Evidências científicas incontestáveis incluem: fotos de satélites, observações astronômicas, medições de sombras, viagens ao redor do mundo e experimentos de física. A teoria da Terra plana é uma pseudociência sem fundamento.

Fonte: Boatos.org - https://www.boatos.org/
Data: 2024
""",
            "g1_politica": """
NOTÍCIA: Governo brasileiro aprova nova lei de proteção de dados

O Congresso Nacional aprovou nesta terça-feira (15) uma nova lei que fortalece a proteção de dados pessoais no Brasil. A medida estabelece regras mais rígidas para o tratamento de informações pessoais por empresas e órgãos públicos.

A lei prevê multas de até 2% do faturamento da empresa em caso de vazamento de dados, limitadas a R$ 50 milhões por infração.

Fonte: G1 - https://g1.globo.com/
Data: 2024
""",
            "folha_ciencia": """
NOTÍCIA: Aquecimento global é realidade científica

Pesquisas científicas confirmam que o aquecimento global é uma realidade causada principalmente pela atividade humana. Dados da NASA mostram que a temperatura média da Terra aumentou 1,1°C desde 1880, com os últimos 7 anos sendo os mais quentes já registrados.

As principais causas incluem emissões de gases de efeito estufa, desmatamento e queima de combustíveis fósseis.

Fonte: Folha de S.Paulo - https://www1.folha.uol.com.br/
Data: 2024
""",
            "verificacao_eleicoes": """
VERIFICAÇÃO: Eleições brasileiras são seguras e confiáveis

VERDADEIRO. O sistema eleitoral brasileiro é considerado um dos mais seguros do mundo. A urna eletrônica possui múltiplas camadas de segurança, incluindo criptografia, auditoria e verificação independente. Não há evidências de fraude nas eleições brasileiras.

Fonte: TSE (Tribunal Superior Eleitoral)
Data: 2024
""",
            "verificacao_saude": """
VERIFICAÇÃO: Exercícios físicos melhoram a saúde mental

VERDADEIRO. Estudos científicos comprovam que exercícios físicos regulares melhoram significativamente a saúde mental, reduzindo sintomas de ansiedade e depressão. A atividade física libera endorfinas e outros neurotransmissores que promovem bem-estar.

Fonte: Organização Mundial da Saúde (OMS)
Data: 2024
""",
            "verificacao_economia": """
VERIFICAÇÃO: Inflação no Brasil está controlada

PARCIALMENTE VERDADEIRO. A inflação no Brasil apresentou redução significativa em 2024, mas ainda está acima da meta do Banco Central. O IPCA acumulado em 12 meses ficou em 4,5%, próximo ao centro da meta de 4,25% com tolerância de 1,5 ponto percentual.

Fonte: IBGE e Banco Central do Brasil
Data: 2024
"""
        }
    
    def ingest_from_url(self, url: str, source_name: str = "web") -> bool:
        """
        Ingesta dados de uma URL específica.
        
        Args:
            url: URL para baixar
            source_name: Nome da fonte
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info(f"Ingerindo dados de: {url}")
            
            # Fazer requisição
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair texto
            text = soup.get_text()
            
            # Limpar texto
            text = self._clean_text(text)
            
            # Salvar arquivo
            file_path = self.data_path / f"{source_name}_{int(time.time())}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"URL: {url}\n")
                f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Fonte: {source_name}\n\n")
                f.write(text)
            
            logger.info(f"Dados salvos: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao ingerir dados de {url}: {str(e)}")
            return False
    
    def ingest_from_file(self, file_path: str, source_name: str = "file") -> bool:
        """
        Ingesta dados de um arquivo local.
        
        Args:
            file_path: Caminho do arquivo
            source_name: Nome da fonte
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info(f"Ingerindo dados de arquivo: {file_path}")
            
            # Ler arquivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Salvar na pasta de dados
            file_name = Path(file_path).name
            dest_path = self.data_path / f"{source_name}_{file_name}"
            
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(f"Arquivo original: {file_path}\n")
                f.write(f"Data: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Fonte: {source_name}\n\n")
                f.write(content)
            
            logger.info(f"Arquivo copiado: {dest_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao ingerir arquivo {file_path}: {str(e)}")
            return False
    
    def _clean_text(self, text: str) -> str:
        """
        Limpa e normaliza texto extraído.
        
        Args:
            text: Texto bruto
            
        Returns:
            Texto limpo
        """
        # Remover quebras de linha excessivas
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        # Remover caracteres especiais
        text = text.replace('\r', '')
        text = text.replace('\t', ' ')
        
        # Normalizar espaços
        text = ' '.join(text.split())
        
        return text
    
    def get_ingestion_status(self) -> Dict[str, Any]:
        """
        Retorna status da ingestão de dados.
        
        Returns:
            Dicionário com status
        """
        try:
            files = list(self.data_path.glob("*.txt"))
            
            return {
                "data_path": str(self.data_path),
                "num_files": len(files),
                "files": [f.name for f in files],
                "total_size": sum(f.stat().st_size for f in files),
                "last_updated": max(f.stat().st_mtime for f in files) if files else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {str(e)}")
            return {
                "data_path": str(self.data_path),
                "num_files": 0,
                "files": [],
                "total_size": 0,
                "last_updated": 0,
                "error": str(e)
            }
    
    def create_sample_html(self) -> bool:
        """
        Cria arquivos HTML de exemplo para demonstração.
        
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            logger.info("Criando arquivos HTML de exemplo...")
            
            # Dados HTML de exemplo
            html_samples = {
                "verificacao_covid.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Verificação: Vacinas COVID-19</title>
</head>
<body>
    <h1>VERIFICAÇÃO: Vacinas contra COVID-19 são seguras</h1>
    <p><strong>VERDADEIRO.</strong> As vacinas contra COVID-19 são seguras e eficazes, conforme comprovado por estudos científicos rigorosos.</p>
    <p>Dados da OMS mostram que mais de 13 bilhões de doses foram administradas globalmente com segurança.</p>
    <p>Fonte: Organização Mundial da Saúde (OMS)</p>
    <p>Data: 2024</p>
</body>
</html>
""",
                "verificacao_clima.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Verificação: Mudanças Climáticas</title>
</head>
<body>
    <h1>VERIFICAÇÃO: Mudanças climáticas são causadas pelo homem</h1>
    <p><strong>VERDADEIRO.</strong> O consenso científico é claro: as mudanças climáticas são causadas principalmente pela atividade humana.</p>
    <p>Dados da NASA mostram que a temperatura média global aumentou 1,1°C desde 1880.</p>
    <p>Fonte: NASA e IPCC</p>
    <p>Data: 2024</p>
</body>
</html>
"""
            }
            
            # Salvar arquivos HTML
            for filename, content in html_samples.items():
                file_path = self.data_path / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Arquivo HTML criado: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar arquivos HTML: {str(e)}")
            return False

