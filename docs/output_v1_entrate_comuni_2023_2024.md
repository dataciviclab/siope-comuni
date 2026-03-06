# Output v1 - entrate comuni 2023-2024

## Perimetro

- fonte: `siope_entrate_comuni_agg_labeled`
- annualita': `2023`, `2024`
- taglio: comuni
- filtro analitico di partenza: `is_titolo_9 = false`
- unita' di misura: euro (`importo_totale_eur`)

## Domande iniziali

1. I grandi comuni mostrano profili di entrata simili o fortemente diversi?
2. Quanto pesano le entrate tributarie proprie rispetto ai trasferimenti?
3. Quali comuni crescono o calano di piu' tra `2023` e `2024` una volta tolte le voci tecniche?

## Grandi comuni - totale entrate non tecniche

| Ente | Totale 2023 (EUR) | Totale 2024 (EUR) | Delta % |
| --- | ---: | ---: | ---: |
| ROMA CAPITALE | 5.566.885.808,40 | 6.053.187.576,98 | 8,74% |
| COMUNE DI MILANO | 3.793.719.953,70 | 4.292.310.503,04 | 13,14% |
| COMUNE DI NAPOLI | 1.998.537.883,76 | 1.798.842.159,95 | -9,99% |
| COMUNE DI TORINO | 1.744.902.350,32 | 1.674.966.542,07 | -4,01% |
| COMUNE DI GENOVA | 1.137.745.982,84 | 1.222.985.575,36 | 7,49% |
| COMUNE DI FIRENZE | 817.390.549,55 | 1.025.835.082,42 | 25,50% |
| COMUNE DI VENEZIA | 903.653.958,22 | 945.093.048,23 | 4,59% |
| COMUNE DI BOLOGNA | 756.114.877,62 | 939.510.574,35 | 24,26% |
| COMUNE DI PALERMO | 1.284.474.100,60 | 890.909.980,19 | -30,64% |
| COMUNE DI CATANIA | 455.439.056,60 | 606.535.141,33 | 33,18% |

## Lettura rapida

- Roma e Milano restano nettamente sopra gli altri, ma la crescita 2024 e' piu' forte a Milano in termini percentuali.
- Firenze, Bologna e Catania mostrano crescite molto visibili.
- Napoli, Torino e Palermo scendono anche dopo il filtro sulle voci tecniche, quindi il segnale merita approfondimento.

## Top voci complessive 2024 senza titolo 9

| Codice voce | Descrizione | Totale 2024 (EUR) |
| --- | --- | ---: |
| `1.01.01.06.001` | Imposta municipale propria riscossa a seguito dell'attivita' ordinaria di gestione | 15.479.777.438,64 |
| `1.03.01.01.001` | Fondi perequativi dallo Stato | 7.150.604.174,94 |
| `2.01.01.02.001` | Trasferimenti correnti da Regioni e province autonome | 6.820.693.993,16 |
| `1.01.01.51.001` | Tassa smaltimento rifiuti solidi urbani riscossa a seguito dell'attivita' ordinaria di gestione | 6.673.258.615,32 |
| `4.02.01.01.001` | Contributi agli investimenti da Ministeri | 6.637.227.843,73 |
| `1.01.01.16.001` | Addizionale comunale IRPEF riscossa a seguito dell'attivita' ordinaria di gestione | 6.422.410.154,19 |
| `2.01.01.01.001` | Trasferimenti correnti da Ministeri | 5.033.795.825,21 |
| `4.02.01.02.001` | Contributi agli investimenti da Regioni e province autonome | 3.779.200.302,86 |
| `1.01.01.61.001` | Tributo comunale sui rifiuti e sui servizi | 2.890.767.568,36 |
| `7.01.01.01.001` | Anticipazioni da istituto tesoriere/cassiere | 2.606.164.640,49 |

## Prime tre voci 2024 nei maggiori comuni

### ROMA CAPITALE

- `1.01.01.06.001` IMU: `1.204.124.913,80` EUR
- `1.01.01.61.001` Tributo comunale sui rifiuti e sui servizi: `822.605.554,96` EUR
- `2.01.01.01.001` Trasferimenti correnti da Ministeri: `652.756.589,09` EUR

### COMUNE DI MILANO

- `1.01.01.06.001` IMU: `905.911.992,81` EUR
- `3.01.02.01.043` Proventi per traffico e trasporto passeggeri e utenti: `386.146.461,05` EUR
- `2.01.01.02.999` Trasferimenti correnti da altre Amministrazioni Locali n.a.c.: `368.848.989,33` EUR

### COMUNE DI NAPOLI

- `1.03.01.01.001` Fondi perequativi dallo Stato: `331.570.407,01` EUR
- `2.01.01.01.001` Trasferimenti correnti da Ministeri: `232.384.329,32` EUR
- `1.01.01.06.001` IMU: `227.582.770,33` EUR

### COMUNE DI TORINO

- `1.01.01.06.001` IMU: `254.240.643,36` EUR
- `2.01.01.01.001` Trasferimenti correnti da Ministeri: `200.022.713,71` EUR
- `1.01.01.51.001` Tassa smaltimento rifiuti solidi urbani: `195.857.232,70` EUR

### COMUNE DI GENOVA

- `1.01.01.06.001` IMU: `172.183.310,04` EUR
- `4.02.01.01.001` Contributi agli investimenti da Ministeri: `172.078.071,68` EUR
- `1.01.01.51.001` Tassa smaltimento rifiuti solidi urbani: `150.017.594,00` EUR

## Prime letture utili

- la composizione delle entrate dei grandi comuni non e' omogenea
- una parte del delta `2023 -> 2024` sembra guidata da trasferimenti e contributi agli investimenti, non solo da tributi propri
- per alcuni enti il segnale di calo resta visibile anche dopo il filtro sulle voci tecniche

## Limiti di lettura

- questo output non include `uscite`
- il filtro `is_titolo_9 = false` e' metodologico, non una pulizia dei dati
- il titolo `7.*` resta dentro il perimetro e va letto con cautela a seconda della domanda
- alcuni debiti tecnici restano aperti nel backlog del progetto
