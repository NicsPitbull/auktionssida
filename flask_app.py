# flask_app.py
"""
HUVUDFIL FÖR FLASK-APPLIKATIONEN (Applikationens Nav)

SYFTE: Att initiera och konfigurera alla delar (databaser, inloggning, moduler)
som applikationen behöver för att fungera.

DESIGNPRINCIP: Denna fil följer "Application Factory Pattern" (skapa_app),
vilket är bäst praxis för att skapa en skalbar och testbar Flask-applikation.

SINGLE RESPONSIBILITY:
1. Skapa Flask-applikationen.
2. Konfigurera applikationen (inställningar).
3. Initiera databas och inloggning.
4. Registrera alla blueprints.
5. Definiera routes för huvudnivån (t.ex. startsidan).
6. Starta applikationen.
"""
from flask import Flask, render_template
from flask_login import LoginManager
import os  # Importera os-modulen för att använda os.environ.get
# Importera init_db-funktionen som sätter upp SQLAlchemy (databasen)
from database import init_db

def skapa_app():
    """
    Application Factory: Skapar och konfigurerar Flask-applikationen.

    Returns:
        Flask: Den färdiga Flask-applikationen-instansen.
    """
    # 1. Skapa Flask-appen
    app = Flask(__name__)

    # >>> ÄNDRING HÄR: Hämta den absoluta sökvägen till projektmappen
    # __file__ är sökvägen till flask_app.py. Vi tar katalogen (dirname).
    project_dir = os.path.abspath(os.path.dirname(__file__))
    
    # ============================================================
    # 2. KONFIGURATION (Applikationsinställningar)
    # ============================================================
    # SECRET_KEY: Nödvändig för att skydda session cookies (inloggning). BYT DENNA I PRODUKTION!
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'din_superhemliga_nyckel')
    
    # SQLALCHEMY_DATABASE_URI: Anger vilken databas vi ska använda (en SQLite-fil).
    # >>> KORRIGERAD SÖKVÄG FÖR DEPLOYMENT: Använder ABSOLUT sökväg till databasfilen
    db_path = os.path.join(project_dir, 'blgeestates.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
    
    # SQLALCHEMY_TRACK_MODIFICATIONS: Stängs av för att spara resurser (bäst praxis).
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ============================================================
    # 3. INITIERA DATABASEN
    # ============================================================
    # init_db: Anropar funktionen som kopplar SQLAlchemy till appen och skapar tabellerna.
    init_db(app)

    # ============================================================
    # 3.5. INITIERA FLASK-LOGIN
    # ============================================================
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from dbrepositories.user_repository import UserRepository
        user_repo = UserRepository()
        return user_repo.get_by_id(int(user_id))

    # ============================================================
    # 4. REGISTRERA BLUEPRINTS
    # ============================================================
    # Anropar hjälpfunktionen som kopplar alla moduler till appen.
    registrera_blueprints(app)

    # ============================================================
    # 5. REGISTRERA ROUTES (URL:er för hela appen)
    # ============================================================
    # Anropar hjälpfunktionen som definierar startsidor och huvud-rutter.
    create_routes(app)

    return app


def registrera_blueprints(app):
    """
    Registrerar alla blueprints i applikationen.
    Kopplar ihop de separata modulerna (Blueprints) med huvudapplikationen.

    Args:
        app (Flask): Flask-applikationen
    """
    # Importera blueprint-objekten från deras respektive moduler
    from myblueprints.auctions import auctions_bp
    from myblueprints.bidding import bidding_bp
    from myblueprints.auth import auth_bp
    from myblueprints.admin import admin_bp
    from myblueprints.pages import pages_bp

    # app.register_blueprint: Den faktiska kopplingen sker här.
    # url_prefix: Anger det prefix som alla routes i blueprintet kommer att ha.
    app.register_blueprint(auctions_bp, url_prefix='/auctions')
    app.register_blueprint(bidding_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(pages_bp)


def create_routes(app):
    """
    Skapar routes som hör till hela appen (globala routes).

    Args:
        app (Flask): Flask-applikationen
    """

    @app.route("/hello")
    def hello_world():
        """En enkel test-rutt."""
        return "<p>Hej Världen! Min första Flask-app!</p>"

    @app.route('/')
    def index():
        """Startsidan."""
        # render_template: Letar efter home.html i mappen 'templates' i roten
        return render_template('home.html', titel='Välkommen')


# ============================================================
# STARTPUNKT
# ============================================================
# Anropar Application Factory för att bygga hela appen
app = skapa_app()

if __name__ == '__main__':
    # Kör applikationen!
    # debug=True: Aktiverar debug-läget, vilket gör att koden laddas om vid ändring i vscode
    app.run(debug=True)