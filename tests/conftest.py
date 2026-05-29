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
