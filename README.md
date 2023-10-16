# PokemonTCG-Card-Network

**Projeto da disciplina de Redes Sociais**

**Alunos**: 
- Arthur Barreto
- Enricco Gemha
- Felipe Catapano

## Descrição do Projeto

O projeto tem como objetivo analisar a influência das cartas usadas pelos jogadores de Pokémon TCG, verioficando se as cartas usadas pelos jogadores inflênciam no ranking obtido pelos jogadores.

Para criar a base de dados foi feito um webscraping, extraindo os dados do site [LimitlessTCG](https://limitlesstcg.com/),considerando as seguintes restrições:
- todos os jogos de todos os campeonatos oficiais a partir de 2011
- o id do usuário que utilizou a carta
- o ranking que o deck ficou naquele campeonato
- o id da carta utilizada, sempre trocando pela versão com menor raridade

### Conceito de aresta e vértices

Para o conceito de **vértices** foi adotado:
- Cada carta é um vértice. Para cartas com mesmo texto, ou seja, sem diferença em jogo, porém esteticamente diferentes, vamos considerar como a mesma carta.

Para o conceito de **aresta** foi adotado:
- Duas cartas estão relacionadas se estão no mesmo deck (baralho).
- O peso da aresta entre duas cartas é o número de decks em que ambas estão listadas.

### Variáveis

Como variáveis de análise temos:

- id_card : identificador único de cada carta presente em cada deck;
- id_tournament : identificador único do torneio no qual o deck participou;
- id_player : identificador único do jogador que usou determinado deck;
- tournament_rank : posição do deck no torneio que disputou;
- tournament_type : tipo de torneio que foi disputado (ex.: Mundial, Internacional, Nacional, Regional, torneios menores);

### Hipótese

Uma maior sinergia entre cartas leva a uma maior chance de ganhar um torneio. Sinergia é o quanto duas cartas combinam, para serem usadas no mesmo deck. Representamos a sinergia pelo peso da arestas, que é em quantos decks essas cartas foram usadas juntas, porque sabemos que cartas com alta sinergia são usadas juntas.

Para visualizar o peso de cada vértice, veremos seu **poder**, levando em consideração as variáveis: 
- tournament_type;
- tournament_rank;
- copy_rate (quantidade de vezes que ela aparece repetida no mesmo deck).
