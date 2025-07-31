## UML Class Diagram

### To generate a png, use this in the root of the project:
```powershell
pyreverse -o png -p game ./src/ptcgp_sim
```

### Example UML Class Diagram
```
+----------------+       1..2 +-----------+       1 +-----------------+
| GameController |<>----------|  Player   |<>-------|      Deck       |
+----------------+            +-----------+         +-----------------+
| - player1      |            | - name    |         | - cards: List   |
| - player2      |            | - bench   |         +-----------------+
| - ruleEngine   |            | - hand    |                   | 1..*
+----------------+            | - deck    |                   |
        |                     +-----------+                   |
        |                           | 0..*                    v
        |                           |                     +-----------+
        v                           |                     |   Card    |
+----------------+                  |                     +-----------+
|   RuleEngine   |                  +---------------------| - name    |
+----------------+                                        | - stats   |
| - rules: List  |                                        +-----------+
+----------------+
        | 1..*
        v
+----------------+
|      Rule      |
+----------------+
| + condition()  |
| + action()     |
+----------------+
```
