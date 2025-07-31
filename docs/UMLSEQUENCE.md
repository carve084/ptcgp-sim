## Sequence Diagram for Card Attack and Death Handling
```
:PlayerUI   :GameController   :Attacker(Card)   :Defender(Card)   :RuleEngine      :Rule
    |               |                 |                 |              |
    | requestAttack(attacker, defender)                 |              |
    |-------------> |                 |                 |              |
    |               | validateMove()  |                 |              |
    |               |---------------->|                 |              |
    |               |  (valid)        |                 |              |
    |               | <---------------|                 |              |
    |               |                 |                 |              |
    |               | resolveAttack(attacker, defender) |              |
    |               |---------------------------------->|              |
    |               |                 |                 |              |
    |               |                 | takeDamage(atk_points)         |
    |               |                 |---------------->|              |
    |               |                 |                 |              |
    |               |                 | (Defender dies) |              |
    |               |                 |                 |              |
    |               |                 |                 | OnDeath()    |
    |               |                 |                 |------------> | (Event broadcast)
    |               |  handleCardDeath(defender)        |              |
    |               | <------------------------------------------------| (Subscriber receives event)
    |               |                 |                 |              |
    |               | createEvent("CARD_DIED", defender)|              |
    |               |---------------->|                 |              |
    |               | processEvent(event)               |
    |               |------------------------------------------------->|
    |               |                 |                 |              | findRules()
    |               |                 |                 |              |------------>|
    |               |                 |                 |              |  (ExRule)
    |               |                 |                 |              | <-----------|
    |               |                 |                 |              |
    |               |                 |                 |              | executeAction()
    |               |                 |                 |              |------------>|
    |               |                 |                 |              |             |
    |               |  (Controller updates Player state based on rule outcome)       |
    |               | <--------------------------------------------------------------|
    |               |                 |                 |              |
```