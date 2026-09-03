---
title: Como Nascem os Produtos Digitais
subtitle: Do problema ao lançamento, e o papel da inteligência artificial
author: Engenharia de Software para o Negócio
date: Setembro de 2026
---

## Agenda

- Da ideia ao produto no ar
- Quem faz o quê
- Trabalhando em ciclos rápidos
- Inteligência artificial no software
- Caso prático: uma corretora de seguros

::: notes
Abertura: o objetivo desta conversa é desmistificar como um produto ou uma
funcionalidade nasce, quem participa e como a inteligência artificial está
mudando o que conseguimos entregar. Linguagem de negócio, sem jargão técnico.
:::

# Da ideia ao produto no ar

## O que chamamos de "produto" e de "funcionalidade"

- Produto: a solução completa que entrega valor ao cliente (um aplicativo, um sistema, um serviço digital)
- Funcionalidade: uma capacidade específica dentro desse produto (por exemplo, "consultar uma apólice" ou "simular um seguro")
- Todo produto é feito de várias funcionalidades, construídas e entregues aos poucos
- Cada uma delas passa por um ciclo parecido, do problema até o uso real pelo cliente

## O ciclo de vida, do início ao fim

![](assets/diagrama_ciclo_vida.png){width=92%}

::: notes
Este é o mapa mental de toda a apresentação. Toda funcionalidade, por menor
que seja, passa por essas seis etapas, e o aprendizado de uma rodada alimenta
a próxima oportunidade.
:::

## Como nasce uma nova funcionalidade

- Alguém identifica uma oportunidade: um problema do cliente, um pedido do mercado ou um número que chama atenção
- Essa oportunidade vira uma hipótese: "se resolvermos isso, geramos este resultado"
- As hipóteses são priorizadas: nem tudo pode ser feito ao mesmo tempo, então escolhemos o que traz mais valor primeiro
- Só depois disso o time começa a desenhar a solução

## Da definição ao lançamento

- A solução é desenhada em conjunto, com entradas de negócio e de tecnologia
- A construção acontece em pedaços pequenos, não em um único bloco gigante
- Cada pedaço é testado com usuários reais antes de seguir adiante
- O lançamento costuma ser gradual: primeiro para poucos clientes, depois para todos
- Depois de lançado, os resultados são acompanhados de perto para decidir os próximos passos

# Quem faz o quê

## Três papéis, um objetivo em comum

![](assets/diagrama_papeis.png){width=92%}

## Product Owner: a voz do negócio e do cliente

- Entende profundamente o cliente, o mercado e a estratégia do negócio
- Decide o que deve ser feito primeiro, com base no valor gerado
- É o ponto de contato entre as áreas de negócio e o time que constrói a solução
- Garante que o time esteja sempre resolvendo o problema certo

## System Engineer: a costura entre os sistemas

- Olha para o produto de forma ampla, além de uma única funcionalidade
- Garante que as diferentes partes do sistema conversem entre si sem atrito
- Cuida da integração com sistemas de parceiros e de outras áreas da empresa
- Pensa em crescimento futuro: a solução precisa continuar funcionando bem quando o uso aumentar

## Tech Lead: qualidade e liderança técnica

- Lidera o time responsável por construir a solução no dia a dia
- Decide, junto com o time, a melhor forma técnica de resolver cada problema
- Cuida da qualidade, da segurança e da manutenção do que é construído
- Ajuda a estimar prazos e a identificar riscos antes que eles virem problemas

# Trabalhando em ciclos rápidos

## O que são metodologias ágeis, em termos simples

- São formas de organizar o trabalho em ciclos curtos, em vez de um grande projeto fechado
- A cada ciclo, o time entrega algo que pode ser mostrado e avaliado
- O plano se ajusta com frequência, a partir do que se aprende com clientes reais
- O objetivo é reduzir o risco de investir muito tempo em algo que o mercado não quer

## Pequenas entregas, feedback constante

- O trabalho é dividido em ciclos de poucas semanas
- Ao final de cada ciclo, o time mostra o que foi construído e recebe feedback
- Problemas são identificados cedo, quando ainda são baratos e fáceis de corrigir
- A equipe de negócio acompanha o progresso de perto, sem surpresas no final

## Ciclo de validação rápida

- Antes de construir a solução completa, testamos uma versão simples da ideia
- Essa versão é colocada na frente de clientes reais o quanto antes
- Os resultados reais substituem suposições: aprendemos o que funciona de verdade
- Só investimos pesado depois de validar que a ideia gera o resultado esperado

## Por que isso importa para o negócio

- Reduz o risco de gastar tempo e dinheiro em algo que ninguém vai usar
- Acelera o tempo entre a ideia e o valor entregue ao cliente
- Dá visibilidade constante ao negócio sobre o andamento do trabalho
- Permite mudar de direção rapidamente quando o mercado muda

# Inteligência artificial no software

## IA como uma nova camada dos produtos digitais

- Até pouco tempo atrás, sistemas seguiam apenas regras fixas, escritas por pessoas
- Hoje, a inteligência artificial permite que sistemas entendam linguagem natural e respondam de forma mais flexível
- Isso abre espaço para assistentes que conversam com o cliente, resumem informações e ajudam pessoas a decidir mais rápido
- O desafio deixou de ser "o sistema entende o pedido?" e passou a ser "a resposta é confiável?"

## Duas formas de a IA consultar informação

![](assets/diagrama_rag_graphrag.png){width=95%}

::: notes
RAG: o assistente busca em documentos relevantes antes de responder, como um
bom atendente que consulta o manual certo. GraphRAG vai além: entende como as
informações se conectam entre si, como um mapa de relacionamentos, o que
ajuda a responder perguntas mais complexas.
:::

# Caso prático: uma corretora de seguros

## O contexto: NovaSeguro Corretora (exemplo fictício)

- A NovaSeguro trabalha com várias seguradoras parceiras ao mesmo tempo
- Cada seguradora tem suas próprias regras, apólices, coberturas e prazos
- Os corretores precisam responder perguntas de clientes com rapidez e precisão
- Hoje, essa informação está espalhada entre manuais, planilhas e sistemas diferentes

## O desafio do dia a dia

- Encontrar a informação certa toma tempo e depende de quem está de plantão
- É difícil comparar coberturas entre seguradoras diferentes na hora da conversa com o cliente
- Perguntas mais complexas, como possíveis sobreposições de cobertura, quase nunca são respondidas na hora
- O resultado é atendimento mais lento e risco de informação incorreta

## A solução: um assistente inteligente para os corretores

![](assets/diagrama_fluxo_ia.png){width=90%}

## Começando simples: consulta a documentos

- O assistente é treinado para consultar manuais, apólices e contratos das seguradoras parceiras
- Quando o corretor faz uma pergunta, ele busca a informação nos documentos certos
- A resposta sempre indica de onde veio a informação, para gerar confiança
- Essa é a base: uma forma de a IA responder com apoio em fontes confiáveis, e não apenas "adivinhar"

## Evoluindo: entendendo as conexões entre as informações

- Com o tempo, a NovaSeguro passa a mapear como as informações se relacionam: clientes, apólices, coberturas, sinistros e seguradoras
- Isso permite responder perguntas mais ricas, como identificar sobreposições de cobertura entre seguradoras diferentes
- O assistente passa a enxergar o panorama completo do cliente, e não apenas um documento isolado
- É um salto de "responder perguntas" para "gerar recomendações de negócio"

## Benefícios para o negócio

- Atendimento mais rápido, com menos tempo de espera para o cliente
- Menos erros por informação desatualizada ou mal interpretada
- Decisões melhores, apoiadas em uma visão mais completa do cliente
- Integração mais simples com os sistemas de cada seguradora parceira

## Cuidados importantes

- A qualidade da resposta depende da qualidade dos dados usados como fonte
- Pessoas continuam responsáveis por revisar decisões de maior impacto
- É preciso definir regras claras de acesso e uso da informação dos clientes
- Inteligência artificial é uma ferramenta poderosa, mas não substitui a governança do negócio

# Mensagens-chave

## O que vale levar desta conversa

- Todo produto e toda funcionalidade seguem um ciclo, da oportunidade ao aprendizado
- Product Owner, System Engineer e Tech Lead olham para o mesmo problema sob ângulos diferentes
- Ciclos curtos e validação rápida reduzem risco e aceleram resultados
- A inteligência artificial adiciona uma nova camada de valor, mas exige dados confiáveis e boa governança

# Obrigado
