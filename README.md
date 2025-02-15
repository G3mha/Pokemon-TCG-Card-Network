# A Network-oriented Analysis of the Pokémon TCG Competitive Scene

![Pokémon TCG](wallpaper.jpg)

This project was developed for the Social Networks course in the Computer Engineering program at Insper (2023/2 semester).

**Authors**:

- [Arthur Barreto](https://github.com/Arthur-Barreto)
- [Enricco Gemha](https://github.com/G3mha)
- [Felipe Catapano](https://github.com/MekhyW)

🇧🇷 Version in Portuguese: [click here](./README-pt_BR.md)

## Glossary

- Deck = collection of cards used for play
- Set = collection of cards released together
- Pokémon® TCG = Pokémon Trading Card Game®
- Vanilla = standard/basic version
- Card Types = Pokémon, Trainer, Energy
- Standard Format = official game format that allows the use of cards released from a specific collection onward. It is updated annually, and older cards are removed from the format
- Card Versions = cards that have purely aesthetic changes but possess the same properties. For example, some cards have a vanilla version and a full art version
- Card Code = unique identifier for the card model in a specific collection. Can be found in the lower left corner of the card

## Project Description

The project aims to analyze the influence of cards used by competitive Pokémon TCG players, examining their impact on players' rankings. If you want to learn more about the game, see this article from [Pokémon Blast News](https://www.jacobmarciniec.com/blog/pokemon-cards-explained-for-absolute-beginners). For this purpose, we generated a network that relates cards based on a database containing their information.

To create the database, we performed web scraping of data from [LimitlessTCG](https://limitlesstcg.com/), a site that provides extensive information about the game's competitive scene.

We emphasize that the extracted data refers to all official championships held between 2011 and 2023.

We will ignore energy cards since they are present in all decks and therefore don't necessarily impact a deck's performance, but rather complement its strategy. No deck is designed with a focus on energy cards, but rather on Pokémon or Trainer cards, which will require specific energy to be used.

Cards that have multiple versions with purely aesthetic changes were considered identical. For the purpose of unique card identification, we considered the code of their oldest vanilla version, meaning the version most commonly found in packs available for sale in the earliest collection that released this card. Let's better understand how this works:

*"The card below has three versions, each with identical properties but with changes in artwork, embossing, and card code (MEW003, MEW182, MEW198). Therefore, when MEW182 and MEW198 appear in a deck, we will use the id MEW003 to represent them."*

![Card MEW003](https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/MEW/MEW_003_R_EN_LG.png)
![Card MEW182](https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/MEW/MEW_182_R_EN_LG.png)
![Card MEW198](https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/MEW/MEW_198_R_EN_LG.png)

*"The second case where this occurs is for cards that were printed in more than one collection. In the case below, card SVI196 was released in 2023, while DEX102 was released in 2012. Both are valid for use in the Standard format of the game. Therefore, when card SVI196 appears, we will use the id DEX102 to identify it."*

![Card SVI196](https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/SVI/SVI_196_R_EN_LG.png)
![Card DEX102](https://limitlesstcg.nyc3.digitaloceanspaces.com/tpci/DEX/DEX_102_R_EN_LG.png)

### Concept of Edges and Vertices

For the concept of **vertices**, we adopted that:

- Each card is a vertex, without distinction between identical cards of different rarity, or cards that were reprinted.

For the concept of **edges**, we adopted that:

- Two cards have a relationship (edge) if they are present in the same deck.
- The weight of the edge between two cards is the number of decks in which both are listed.

### Variables

As analysis variables we have:

- `id_card`: unique identifier for each card present in each deck. It follows the format `<set><number>`
- `id_tournament`: unique identifier for the tournament in which the deck participated. It follows the format `<year>_<month>_<day>_<tournament name>`
- `id_player`: unique identifier for the player who used a specific deck. It follows the format used by the LimitlessTCG site `<int greater than or equal to 0>`
- `tournament_rank`: position of the deck in the tournament it competed in. It follows the format `<int greater than 0>`
- `tournament_type`: type of tournament competed in (e.g., World, International, National, Regional, smaller tournaments). It follows the format `<string>`, and has an ordinal characteristic, meaning it's possible to order tournament types according to their importance

### Hypothesis

> "Greater synergy between cards leads to a higher chance of winning a tournament."

Synergy is how well two cards combine to be used in the same deck. We represent synergy by the weight of the edges.
