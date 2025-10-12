
---

# PulmoVision  

### Um sistema de Deep Learning para detecção de doenças pulmonares a partir de raios-X  

## Sobre o projeto  
O **PulmoVision** é um sistema que usa em **redes neurais convolucionais (CNN)** para a **detecção automática de doenças pulmonares** — **tuberculose e pneumonia** — por meio da análise de **imagens de raio-X do tórax**.  

Ele foi desenvolvido utilizando **Django** como framework web e integra um modelo de **Deep Learning** para processar e classificar exames, proporcionando um suporte rápido e eficiente para diagnósticos médicos.  

## Funcionalidades  
✔️ **Upload de imagens de raio-X** para análise  
✔️ **Detecção automática** de doenças pulmonares com CNN  
✔️ **Gestão de usuários e pacientes** com autenticação segura  
✔️ **Histórico de exames** para acompanhamento clínico  
✔️ **Interface intuitiva** para médicos e pesquisadores  

## 🛠 Tecnologias utilizadas  
🔹 **Python 3.x**  
🔹 **Django** - Framework web  
🔹 **TensorFlow/Keras** - Treinamento do modelo de Deep Learning  
🔹 **OpenCV** - Processamento de imagens  
🔹 **MYSQL** - Banco de dados  
🔹 **Bootstrap** - Interface web responsiva  

## Instalação e Configuração  

### 1. Clone o repositório 
```bash
git clone https://github.com/Ximana/PulmoVision.git
cd PulmoVision
```

### 2. Criação do ambiente virtual  
```bsh
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências  
```bash
pip install -r requirements.txt
```

### 4. Aplique as migrações do banco de dados  
```bash
python manage.py migrate
```

### 5. Crie um superusuário (opcional)  
```bash
python manage.py createsuperuser
```

### 6. Execute o servidor  
```bash
python manage.py runserver
```

Agora, acesse **http://127.0.0.1:8000/** no seu navegador. 🎯  

## Como funciona a detecção?  
1. O usuário faz o upload de uma **imagem de raio-X do tórax**.  
2. O modelo CNN processa a imagem e realiza a **classificação**.  
3. O sistema exibe o resultado: **Normal, Pneumonia ou Tuberculose**.  
4. Os exames são salvos para **acompanhamento e histórico**.  

## Exemplo de saída do modelo  
| Imagem | Previsão do modelo | Precisão |
|--------|-------------------|----------|
| Raio-X 1 | Pneumonia | 98% |
| Raio-X 2 | Tuberculose | 95% |
| Raio-X 3 | Normal | 99% |


## Licença  
Este projeto está licenciado sob a **MIT License**.  

## 📞 Contato  
📧 Email: **pauloximana@gmail.com**  
🌐 GitHub: [ximana](https://github.com/Ximana)  

---

