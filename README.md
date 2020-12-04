# Desafio-Fiat-IBM-Behind-the-Code-2020

Bem-vindo! Neste repositório você encontra a minha solução para o Desafio 8 da [Maratona IBM Behind the Code 2020](https://maratona.dev/pt). O Desafio 8 contou com a presença da **Fiat Chrysler Automobiles**.

![alt text](https://github.com/ChristianCFranca/Desafio-Fiat-IBM-Behind-the-Code-2020/blob/main/git-images/carros.png?raw=true)
 
 A maratona IBM Behind the Code 2020 consistiu em uma série de 8 desafios com problemas reais na área de Machine Learning e Data Science. Foram 72 mil pessoas inscritas com 20 mil ativas durantes todos os 8 desafios.
 
 Ao final da maratona fui capaz de conquistar a posição 82° no ranking brasileiro. Fui capaz de permanecer nos top 50 para os Desafios 2 (Uninassau), 6 (LIT), 7 (TNT) e 8 (FCA).

![alt text](https://github.com/ChristianCFranca/Desafio-Fiat-IBM-Behind-the-Code-2020/blob/main/git-images/Ranking.PNG?raw=true)

# O Desafio

*O Grupo FCA, em busca constante de melhoria de qualidade de seus serviços, bem como dar a melhor experiência para seus clientes, busca soluções tecnológicas, através do reconhecimento de voz, para capturar feedbacks e comentários de forma automática, e através de AI, analisar sentimento, e identificar partes relevantes do produto nesta experiência, como por exemplo, sobre motor, desempenho, acabamento, consumo, etc, e assim poder fazer recomendações e melhorar a experiência do usuário de forma evolutiva. Esta solução poderá ser utilizada durante a experiência de seus clientes, teste de engenharia e qualidade.*

Como objetivo principal, espera-se ter um dispositivo inteligente que é capaz de compreender sugestões de um motorista que dirige um veículo Fiat ou Jeep. Esse dispositivo será capaz de analisar o contexto do que está sendo dito em linguagem natural por um motorista, realizar análise de sentimento, e ao final ser capaz de sugerir outros veículos para test-drive ou review, além de sintetizar informações valiosas para equipes de engenharia responsáveis por melhorias nos automóveis.

Neste desafio foram utilizados diversos serviços da IBM Cloud, como o Watson Speech to Text (STT) para a transcrição de áudio, e o Watson Natural Language Understanding (NLU) para extração de entidades textuais e análise de sentimento. As falas do motorista foram processadas em áudio e em texto, e as entidades textuais pertinentes a identificação de componentes, ou critérios de avaliação dos veículos, foram anotadas por um modelo de IA. Esses serviços foram então todos integrados por meio de uma aplicação `Flask`, que além do modelo treinado também entregou uma API REST como solução.

![alt text](https://github.com/ChristianCFranca/Desafio-Fiat-IBM-Behind-the-Code-2020/blob/main/git-images/arquitetura.png?raw=true)

O notebook `IBMToPython.ipynb` contém um passo a passo de como integrar a biblioteca `ibm_watson` em Python de forma que utilizemos sua API para realizar requisições para os serviços do Watson Machine Learning (Speech to Text e Natural Language Understanding). A etapa de treinamento do Watson Machine Learning foi realizada na própria plataforma nuvem da [IBM Cloud](https://cloud.ibm.com/).

Com as chaves das API's em mãos e entendendo como consumi-las, o app `app.py` foi criado utilizando o Framework `Flask`. Sua execução instancia um servidor Web que uma plataforma ou aplicação web pode realizar requisições para se obter a melhor sugestão de veículo baseado na fala e/ou comentário do usuário.

Como a API deveria ser consumida fora da minha rede local, o app foi colocado em produção na plataforma `Cloud Foundry` da IBM, uma plataforma grátis para dar Deploy em aplicações como essa.

A API está ativa até o presente momento e pode ser acessada no endereço https://ibm-btc-desafio8-fca-ccf.mybluemix.net/

## Consuma a API em tempo real

Como foi mencionado, até o presente momento, a API desenvolvida está ativa e pode ser consumida. Recomendo para isto o uso do [Postman](https://www.postman.com/). A rota a ser utilizada deve ser a `https://ibm-btc-desafio8-fca-ccf.mybluemix.net/recommendation`

Na requisição HTTP, o método deve ser `POST` e o Header `Content-Type` deve ser do tipo `multipart/form-data`.

Envie em um campo de nome `car` um dos nomes a seguir, como se de fato estivesse se referindo àquele carro em específico:

- TORO
- ARGO
- FIORINO
- CRONOS
- MAREA
- DUCATO
- RENEGADE

Em seguida, envie um campo de nome `text` com a sua opinião a respeite do carro. Um exemplo seria algo como:
*O fiat Argo é um carro incrível. Os bancos são muitos macios e possuem muita qualidade. Infelizmente o motor é fraco e deixa muito a desejar nas ultrapassagens. Também não gostei do acabamento lateral, é muito feio.*

Sua requisição no Postman deve se assemelhar à seguinte:

![alt text](https://github.com/ChristianCFranca/Desafio-Fiat-IBM-Behind-the-Code-2020/blob/main/git-images/PostmanReq.png?raw=true)

Envie e espere alguns segundos. A primeira requisição após muito tempo da API em espera pode ocasionar um erro. Se este for o caso, só reenviar. Você receberá uma resposta na seguinte forma:

![alt text](https://github.com/ChristianCFranca/Desafio-Fiat-IBM-Behind-the-Code-2020/blob/main/git-images/Response.png?raw=true)

A API encontrou determinadas entidades em sua opinião e as classificou positivamente ou negativamente quanto ao sentimento envolvido em cada uma. No final, recomendou um modelo diferente de carro caso o sentimento geral tenha sido negativo. A recomendação levou em conta os tipos de entidades que receberam nota negativa e a prioridade de recomendação. Mais detalhes podem ser encontrados no [Github oficial do desafio](https://github.com/maratonadev-br/desafio-8-2020).

No lugar do `text`, você pode enviar um arquivo de áudio no formato `.flac` pela key `audio`. O serviço do **Watson Speech to Text** cuidará de transformar o áudio em um arquivo de texto que irá passar como opinião para a API.
