
---

# PulmoVision  

### Um sistema de Deep Learning para detecção de doenças pulmonares a partir de raios-X  

## Sobre o projeto  
O **PulmoVision** é um sistema que usa em **redes neurais convolucionais (CNN)** para a **detecção automática de doenças pulmonares** — **tuberculose, pneumonia e COVID-19** — por meio da análise de **imagens de raio-X do tórax**.  

Ele foi desenvolvido utilizando **Django** como framework web e integra um modelo de **Deep Learning** para processar e classificar exames, proporcionando um suporte rápido e eficiente para diagnósticos médicos.  

## Funcionalidades  
✔️ **Upload de imagens de raio-X** para análise  
✔️ **Detecção automática** de doenças pulmonares com CNN  
✔️ **Gestão de usuários e pacientes** com autenticação segura  
✔️ **Histórico de exames** para acompanhamento clínico  
✔️ **Interface intuitiva** para médicos e pesquisadores  

## 🏗 Estrutura do projeto  
```
PulmoVision/
│
├── requirements.txt                 # Dependências do projeto
├── manage.py                         # Script de gerenciamento Django
├── README.md                         # Documentação do projeto
│
├── pulmovision/                      # Diretório principal do projeto
│   ├── settings.py                    # Configurações do Django
│   ├── urls.py                        # Rotas do sistema
│
├── apps/                              # Aplicativos do projeto
│   ├── core/                          # Funcionalidades gerais
│   ├── usuarios/                      # Gestão de usuários
│   ├── pacientes/                     # Gestão de pacientes
│   ├── detecao/                       # Lógica de detecção de doenças
│       ├── servicos/                   # Implementação do modelo CNN
│       │   ├── detector.py              # Classe base de detecção
│       │   ├── tuberculose.py           # Detector de tuberculose
│       │   ├── pneumonia.py             # Detector de pneumonia
│       │   ├── covid.py                 # Detector de COVID-19
│
├── static/                            # Arquivos estáticos (CSS, JS, imagens)
├── media/                             # Armazena os exames enviados
└── tests/                             # Testes automatizados
```

## 🛠 Tecnologias utilizadas  
🔹 **Python 3.x**  
🔹 **Django** - Framework web  
🔹 **TensorFlow/Keras** - Treinamento do modelo de Deep Learning  
🔹 **OpenCV** - Processamento de imagens  
🔹 **MYSQL** - Banco de dados  
🔹 **Bootstrap** - Interface web responsiva  

## Instalação e Configuração  

### 1️⃣ Clone o repositório  
```bash
git clone https://github.com/Ximana/PulmoVision.git
cd PulmoVision
```

### 2️⃣ Criação do ambiente virtual  
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

### 3️⃣ Instale as dependências  
```bash
pip install -r requirements.txt
```

### 4️⃣ Aplique as migrações do banco de dados  
```bash
python manage.py migrate
```

### 5️⃣ Crie um superusuário (opcional)  
```bash
python manage.py createsuperuser
```

### 6️⃣ Execute o servidor  
```bash
python manage.py runserver
```

Agora, acesse **http://127.0.0.1:8000/** no seu navegador. 🎯  

## 🎯 Como funciona a detecção?  
1️⃣ O usuário faz o upload de uma **imagem de raio-X do tórax**.  
2️⃣ O modelo CNN processa a imagem e realiza a **classificação**.  
3️⃣ O sistema exibe o resultado: **Saudável, Pneumonia, Tuberculose ou COVID-19**.  
4️⃣ Os exames são salvos para **acompanhamento e histórico**.  

## 📊 Exemplo de saída do modelo  
| Imagem | Previsão do modelo | Precisão |
|--------|-------------------|----------|
| 🖼️ Raio-X 1 | Pneumonia | 98% |
| 🖼️ Raio-X 2 | Tuberculose | 95% |
| 🖼️ Raio-X 3 | Normal | 99% |

## ✅ Testes  
Para rodar os testes automatizados:  
```bash
python manage.py test
```

## 👨‍💻 Contribuição  
Fique à vontade para contribuir! Faça um **fork**, crie uma **branch** e envie um **pull request**.  

## 📜 Licença  
Este projeto está licenciado sob a **MIT License**.  

## 📞 Contato  
📧 Email: **pauloximana@gmail.com**  
🌐 GitHub: [Seu Perfil](https://github.com/Ximana)  

---

