# The Isle of Almost There

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/u-ravendell-charm-the-cartographers-a-one-day-00854547)
[![treasure map](https://img.shields.io/badge/map-treasure%20island-gold)](https://make.fun/bounty/u-ravendell-charm-the-cartographers-a-one-day-00854547)
[![deterministic](https://img.shields.io/badge/build-deterministic-green)](https://make.fun/bounty/u-ravendell-charm-the-cartographers-a-one-day-00854547)

A one-day treasure map sprint entry for the
[Charm the Cartographers bounty](https://make.fun/bounty/u-ravendell-charm-the-cartographers-a-one-day-00854547):
a fictional island drawn in sepia ink on warm parchment, charted by one
very lost cartographer in the year 1726.

The island is called **The Isle of Almost There** — because every sailor
who sets out for it gets *almost* there, then finds a polite parrot, a
napping kraken, or three leagues of bad decisions instead. The dotted red
route starts at Port Quibble, wanders past Dead Man's Nap and the grumbling
mountain, stops to admire The Weeping Palm, sidesteps Crabwise Cove, and
finally arrives at the big red X: The Gilded Gull's Hoard. Probably.


## Places on the map

Eight labelled places, each with its own doodle and its own joke:

- **Port Quibble** — the harbour town where the sensible route begins.
- **Mount Grumble** — the grumpy peak in the north, source of the river.
- **The Weeping Palm** — a drooping palm grove on the eastern shore.
- **Crabwise Cove** — a south-eastern bay with a crab walking sideways.
- **Dead Man's Nap** — a shady hollow with three small headstones.
- **The Gilded Gull's Hoard** — the big red X in the north-east.
- **Siren's Laundry** — a sea rock in the south with washing on the line.
- **The Polite Parrot's Perch** — a cliff viewpoint in the north. Beware:
  it repeats everything.

Charm extras: an ornate eight-point compass rose, a napping kraken
("Here be napping krakens"), a friendly northern sea serpent, a small
galleon with a foam trail, and a legend that admits the route should not
be trusted.

## How to run

```sh
python3 render_map.py   # writes entry.png (1024x1024, <= 1 MiB)
python3 main.py          # copies entry.png to out/entry.png
```

`render_map.py` needs Pillow and the DejaVu Serif fonts; it is fully
deterministic (seed 1726, no clock, no network), so two runs produce
byte-identical PNGs. `main.py` uses only the Python standard library:
it verifies the PNG signature and the 1 MiB size limit, then copies the
file to `$MAKEFUN_OUTPUT_DIR` (default `out/`).

## License

MIT — see `LICENSE`.
