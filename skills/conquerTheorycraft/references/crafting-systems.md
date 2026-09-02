# Server Crafting Systems: Magic Artisan, Weapon Master, Artisan Ou

Source classification: `target_server_official` (wiki.conqueronline.net;
classicconqueronline.com is excluded per the theorycraft skill), with
supplemental corroboration from `community_reference` and `historical_pre_2_0_reference`
(elitepvpers, co.99.com historical pre-2.0 pages). Verified via direct page
inspection during the 2026-08-31 theorycraft session.

## NPCs and roles

### Artisan Wind (Twin City 421,353)
- **Mechanic:** Chance-based (gamble) upgrades for level (via Meteor /
  Meteor Tear / Dragon Ball) and quality (via Dragon Ball).
- **Success rate:** Not guaranteed. Higher level / higher target quality =
  lower success rate.
- **Cost:** 1 Meteor / Meteor Tear / Dragon Ball per attempt.
- **Failure penalty:** Item durability drops 50% on failure; consumed item
  is lost.
- **Threshold rule:** Equipment above Lv110 requires Dragon Balls (not
  Meteors) for both level and quality upgrades here.
- **Socket side-effect:** Upgrade attempts can add sockets — 1/100 chance
  with Dragon Ball, 1/400 chance with Meteor (1/600 on EU server).

### Magic Artisan (Market 181,209)
- **Mechanic:** Guaranteed upgrades. Required quantity scales with current
  level and current quality; no gamble.
- **Level upgrade:** Meteor / Meteor Tear (quantity depends on item's
  current level).
- **Quality upgrade:** Dragon Ball (quantity depends on item's current
  quality tier).
- **Success rate:** 100% once the required quantity is paid.
- **Socket side-effect:** Same 1/100 (DB) or 1/400 (Meteor) chance per
  successful upgrade attempt — Magic Artisan guarantees the upgrade but
  socket addition remains a dice roll.

### Weapon Master (Market 179,194)
- **Mechanic:** Guaranteed upgrades, level or quality, using 1 Dragon Ball
  per attempt.
- **Restriction:** Only operates on weapons over level 120.
- **Success rate:** 100% per attempt.
- **Socket side-effect:** 1/100 chance per upgrade attempt to add a socket.
- **Use case:** The only guaranteed-upgrade path for weapons above Lv120
  via DB; level 121+ upgrades go here, not Magic Artisan (per wiki).

### Artisan Ou (Bird Island 756,545)
- **Mechanic:** Guaranteed socket addition only — pure socket service, no
  level/quality side-effect.
- **Restriction:** Right-handed weapons only.
- **Cost:** 1 Dragon Ball for the 1st socket, **5 Dragon Balls for the
  2nd**.
- **Success rate:** 100% for socket addition. This is the cleanest,
  cheapest path to add a socket to an existing weapon.

## Quality ladder

```
Normal -> Refined -> Unique -> Elite -> Super
```

Each tier step costs more Dragon Balls than the previous, and the cost
scales with the item's current level (higher level = more DBs per step).

## Level-up mechanics

- Meteors / Meteor Tears raise item level, not quality.
- MeteorTear (id 1088002) is functionally equivalent to 10 Meteors at
  Artisan Wind and Magic Artisan.
- Above Lv110, the upgrade path switches from Meteor to Dragon Ball at
  Artisan Wind and the Equipment Blacksmith — Meteor is no longer usable
  for level upgrades on Lv110+ items at those NPCs.
- Per-step cost in DBs / Meteors scales with current level; the wiki
  describes this as exponential in practice though exact retail TQ rates
  are documented in the "Artisan Swindler" calculator (cooldown.dev).

## Order of operations: quality first vs level first

The consensus theorycraft answer (from wiki, forum threads, and the
Artisan Swindler tool's assumptions) is **quality first, then level**,
when the goal is a higher-tier weapon at a higher level.

Reasoning grounded in the verified mechanics:

1. Quality upgrade cost scales with the item's level — upgrading an Elite
   Lv110 item to Super costs fewer DBs than upgrading an Elite Lv120 item
   to Super, on retail rates.
2. Level upgrades get more expensive as level climbs — pushing 110->115
   is cheaper than 115->120 on the same item.
3. If level comes first, you pay quality-upgrade cost on a higher-level
   base. If quality comes first, you pay level-upgrade cost on a higher
   quality item.

The reverse argument: if you run out of DBs mid-level, you have a usable
Lv115 Elite. If you run out of DBs mid-quality, you have a Lv110 Super
Elite (still usable, lower-tier quality). Both are recoverable.

The wiki explicitly notes: "The higher the level or the quality, the more
meteors (meteor tears) or dragon balls required." — meaning both axes
scale independently, and there is no wiki-stated reason to prefer one
order over the other beyond cost efficiency.

## Socket strategy summary

- **Cheapest guaranteed 1st socket:** Artisan Ou at 1 DB. No level/quality
  effect, no gamble.
- **Cheapest guaranteed 2nd socket:** Artisan Ou at 5 DBs, same caveats.
- **Side-effect socket via upgrade:** Artisan Wind / Magic Artisan /
  Weapon Master — 1/100 chance per upgrade attempt with DBs. Expected
  ~100 DBs per socket if pure upgrade path, so don't rely on it as a
  primary strategy.
- **Combined strategy:** Buy a no-socket Super Lv120 weapon, pay Artisan
  Ou 1 DB for a guaranteed socket, then optionally upgrade level via
  Weapon Master (Lv120+ only) or Artisan Wind with chance. This is
  usually cheaper than gambling on socket side-effects during upgrades.

## Confidence and caveats

- All mechanic tables above are from official Classic Conquer wiki and
  co.99.com historical references — classify as `target_server_official`
  and `historical_pre_2.0_reference` respectively.
- The exact DB/Meteor quantities per level step and per quality step are
  server-customizable. Classic Conquer private servers commonly modify
  these rates. Verify on your server before committing silver.
- The "Artisan Swindler" calculator (cooldown.dev) explicitly states it
  uses retail TQ rates; treat its numbers as an upper bound, not a
  guarantee.