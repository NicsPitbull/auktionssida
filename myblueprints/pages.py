# pages.py
"""
BLUEPRINT FÖR STATISKA SIDOR

SYFTE: Hanterar statiska sidor som "Om Oss" och "Kontakt".
Dessa sidor innehåller information om företaget och kontaktuppgifter.
"""
from flask import Blueprint, render_template

# Skapa blueprint för statiska sidor
pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/om-oss')
def om_oss():
    """
    Visar "Om Oss"-sidan med information om företaget.
    """
    return render_template('om_oss.html', titel='Om Oss')


@pages_bp.route('/kontakt')
def kontakt():
    """
    Visar kontaktsidan med kontaktuppgifter.
    """
    return render_template('kontakt.html', titel='Kontakt')
