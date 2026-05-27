#!/bin/bash

python 01_extrai_dados.py
python 02_upload_s3.py
python 03_linhagem.py
python 04_observabilidade.py
python 05_qualidade.py
python 06_enriquecimento.py
python 07_governanca.py
