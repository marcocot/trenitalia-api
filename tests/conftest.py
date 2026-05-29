"""Shared pytest fixtures and payload builders."""

from __future__ import annotations


def stop_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "stazione": "ROMA TERMINI",
        "id": "S08409",
        "tipoFermata": "F",
        "programmata": 1772718120000,
        "actualFermataType": 0,
        "progressivo": 0,
    }
    base.update(overrides)
    return base


def status_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "numeroTreno": 9642,
        "compNumeroTreno": "IC 9642",
        "origine": "REGGIO CALABRIA",
        "destinazione": "ROMA TERMINI",
        "compTipologiaTreno": "Intercity",
        "circolante": True,
        "arrivato": False,
        "nonPartito": False,
        "ritardo": 5,
        "compOrarioPartenzaZero": "07:00",
        "compOrarioArrivoZero": "13:30",
        "compRitardo": ["5 minuti"],
        "fermate": [
            stop_payload(
                stazione="REGGIO CALABRIA", id="S00001", tipoFermata="P", actualFermataType=1
            ),
            stop_payload(stazione="NAPOLI CENTRALE", id="S00002"),
            stop_payload(stazione="ROMA TERMINI", id="S00003", tipoFermata="A"),
        ],
    }
    base.update(overrides)
    return base


SEARCH_BODY = "9642 - REGGIO DI CALABRIA CENTRALE - 05/03/26|9642-S11781-1772665200000"


STATION_AUTOCOMPLETE_BODY = "MONCALIERI|S00453\nMONCALIERI SANGONE|S00510\n"


def station_detail_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "key": "S00453_3",
        "codReg": 3,
        "tipoStazione": 3,
        "codiceStazione": "S00453",
        "codStazione": "S00453",
        "lat": 44.998187,
        "lon": 7.678027,
        "localita": {
            "nomeLungo": "MONCALIERI",
            "nomeBreve": "MONCALIERI",
            "label": "Moncalieri",
            "id": "S00453",
        },
        "esterno": False,
    }
    base.update(overrides)
    return base


def departure_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "numeroTreno": 26612,
        "compNumeroTreno": "REG 26612",
        "categoria": "REG",
        "compTipologiaTreno": "regionale",
        "destinazione": "TORINO AEROPORTO DI CASELLE",
        "codOrigine": "S00462",
        "ritardo": 2,
        "circolante": True,
        "arrivato": True,
        "nonPartito": False,
        "inStazione": True,
        "compOrarioPartenza": "10:58",
        "binarioProgrammatoPartenzaDescrizione": "5",
        "binarioEffettivoPartenzaDescrizione": "5",
        "ultimoRilev": 1780045620000,
    }
    base.update(overrides)
    return base


def arrival_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "numeroTreno": 26612,
        "compNumeroTreno": "REG 26612",
        "categoria": "REG",
        "compTipologiaTreno": "regionale",
        "origine": "ASTI",
        "codOrigine": "S00462",
        "ritardo": 2,
        "circolante": True,
        "arrivato": True,
        "nonPartito": False,
        "inStazione": True,
        "compOrarioArrivo": "10:57",
        "binarioProgrammatoArrivoDescrizione": "5",
        "binarioEffettivoArrivoDescrizione": "5",
        "ultimoRilev": 1780045620000,
    }
    base.update(overrides)
    return base


INFOMOBILITY_HTML = """
<ul id="accordionGenericInfomob">
  <li class="editModeCollapsibleElement">
    <a href="#" id="headingNewsAccordion0"
       class="headingNewsAccordion inEvidenza">Linea Ancona - Bologna: ripresa graduale</a>
    <div class="boxAcc">
      <div>
        <div class="textComponent">
          <h4>29.05.2026</h4>
          <div class="info-text  inEvidenza">
            <p>La circolazione &egrave; in graduale ripresa.</p>
            <p>I treni possono registrare ritardi fino a 30 minuti.</p>
          </div>
        </div>
      </div>
    </div>
  </li>
  <li class="editModeCollapsibleElement">
    <a href="#" id="headingNewsAccordion1"
       class="headingNewsAccordion">INFOTRENI FRECCE</a>
    <div class="boxAcc">
      <div>
        <div class="textComponent">
          <h4>29.05.2026</h4>
          <div class="info-text">
            <p>I treni indicati viaggiano con ritardo &gt; 60 minuti.</p>
          </div>
        </div>
      </div>
    </div>
  </li>
</ul>
""".strip()
