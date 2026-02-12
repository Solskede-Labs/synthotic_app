import os
from src.platform_utils import default_recordings_dir


# --- GLOBAL CONFIGURATION ---
APP_NAME = "Synthotic"
VERSION = "0.4.4"
BUILD_DATE = "2026-02-08"
BASE_DIR = default_recordings_dir()
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
LOG_FILE = os.path.join(BASE_DIR, "system.log")

# Audio Constants (Standard for High-Fidelity Speech)
SAMPLE_RATE = 48000
CHANNELS = 2
CHUNK_SIZE = 1024
MODEL_SIZE = "small"  # Balanced for CPU inference speed vs accuracy

# Ensure Base Directory Exists
os.makedirs(BASE_DIR, exist_ok=True)

# --- UI THEME & PALETTE ---
THEME_COLORS = {
    "bg": "#121212",
    "surface": "#1E1E1E",
    "primary": "#00E676",   # Neon Green
    "secondary": "#292929",
    "text": "#E0E0E0",
    "text_dim": "#888888",
    "rec": "#FF5252",       # Recording Red
    "link": "#3498db"       # Hyperlink Blue
}

# --- LOCALIZATION (I18N) ---
LANG_TEXTS = {
    "pt_BR": {
        "status_ready": "Sistema Pronto",
        "status_rec": "Gravando Áudio do Sistema",
        "status_proc": "Processando Transcrição...",
        "status_done": "Transcrição Concluída!",
        "status_err": "Erro Encontrado",
        "sub_ready": "Aguardando comando...",
        "sub_rec": "O áudio da reunião está sendo capturado.",
        "sub_proc": "A IA está convertendo áudio em texto localmente.",
        "sub_done": "Arquivo salvo na pasta de documentos.",
        "btn_rec_start": "🔴 INICIAR GRAVAÇÃO",
        "btn_rec_stop": "⏹ PARAR GRAVAÇÃO",
        "btn_import": "📥 IMPORTAR ARQUIVO",
        "lbl_lang": "Idioma da Interface:",
        "link_folder": "📂 Abrir Pasta de Gravações",
        "tray_open": "Abrir Painel",
        "tray_start": "🔴 Iniciar Gravação",
        "tray_stop": "⏹ Parar e Transcrever",
        "tray_import": "📥 Importar Arquivo",
        "tray_folder": "📂 Abrir Pasta",
        "tray_logs": "📝 Ver Logs",
        "tray_about": "ℹ️ Sobre",
        "tray_exit": "Sair",
        "notify_min_title": "Minimizado",
        "notify_min_msg": "Synthotic continua rodando nos ícones ocultos.",
        "welcome_title": "Bem-vindo ao Synthotic",
        "welcome_head": "Privacidade & Inteligência Local",
        "welcome_body": (
            "Obrigado por instalar o Synthotic.\n\n"
            "Esta ferramenta foi projetada para garantir 100% de privacidade. "
            "Todo o processamento de áudio é feito no seu processador (CPU), "
            "sem enviar dados para nuvens externas.\n\n"
            "Na primeira execução, a IA fará um download único dos modelos neurais."
        ),
        "welcome_dev": "Desenvolvido por:",
        "welcome_btn": "COMEÇAR A USAR",
        "about_desc": "Gravador e Transcritor Autônomo de Reuniões.\nProcessamento Local com Privacidade em Primeiro Lugar.",
        "err_loopback_title": "Dispositivo de Áudio Não Encontrado",
        "err_loopback_msg": "Nenhum dispositivo de loopback de áudio do sistema foi encontrado.\n\nPara gravar o áudio do sistema, habilite um dispositivo de captura do som do sistema (ex.: Stereo Mix no Windows ou monitor do PulseAudio/PipeWire no Linux).\n\nDeseja abrir as configurações de som agora?",
        "err_ffmpeg_title": "Erro no Motor de Áudio",
        "err_ffmpeg_msg": "Falha ao iniciar o motor de gravação de áudio. Verifique se o FFmpeg está instalado corretamente.",
        "settings_title": "Configurações",
        "settings_audio": "Dispositivos de Áudio",
        "settings_loopback": "Áudio do Sistema (Loopback):",
        "settings_mic": "Microfone:",
        "settings_refresh": "Atualizar Dispositivos",
        "settings_folder": "Pasta de Saída",
        "settings_folder_label": "Salvar Gravações em:",
        "settings_browse": "Procurar...",
        "settings_save": "Salvar",
        "settings_cancel": "Cancelar",
        "settings_auto_detect": "(Detecção Automática)",
        "onboarding_welcome_title": "Bem-vindo ao Synthotic",
        "onboarding_welcome_desc": "Configure o Synthotic em 3 passos rápidos para começar a transcrever reuniões com total privacidade.",
        "onboarding_folder_title": "Onde salvar as gravações?",
        "onboarding_folder_desc": "Escolha a pasta onde os arquivos de áudio e transcrições serão salvos.",
        "onboarding_devices_title": "Selecione os Dispositivos de Áudio",
        "onboarding_devices_desc": "Escolha o dispositivo de sistema e microfone. Ambos são obrigatórios.",
        "onboarding_confirm_title": "Confirme as Configurações",
        "onboarding_confirm_desc": "Revise suas escolhas antes de começar:",
        "onboarding_btn_next": "Próximo",
        "onboarding_btn_back": "Voltar",
        "onboarding_btn_finish": "Iniciar Synthotic",
        "onboarding_err_no_folder": "Por favor, selecione uma pasta válida.",
        "onboarding_err_no_devices": "Por favor, selecione ambos os dispositivos de áudio.",
        "language": "pt_BR"
    },
    "en_US": {
        "status_ready": "System Ready",
        "status_rec": "Recording System Audio",
        "status_proc": "Processing Transcription...",
        "status_done": "Transcription Complete!",
        "status_err": "Error Encountered",
        "sub_ready": "Awaiting command...",
        "sub_rec": "Meeting audio is being captured.",
        "sub_proc": "AI is converting audio to text locally.",
        "sub_done": "File saved to documents folder.",
        "btn_rec_start": "🔴 START RECORDING",
        "btn_rec_stop": "⏹ STOP RECORDING",
        "btn_import": "📥 IMPORT FILE",
        "lbl_lang": "Interface Language:",
        "link_folder": "📂 Open Recordings Folder",
        "tray_open": "Open Dashboard",
        "tray_start": "🔴 Start Recording",
        "tray_stop": "⏹ Stop & Transcribe",
        "tray_import": "📥 Import File",
        "tray_folder": "📂 Open Folder",
        "tray_logs": "📝 View Logs",
        "tray_about": "ℹ️ About",
        "tray_exit": "Exit",
        "notify_min_title": "Minimized",
        "notify_min_msg": "Synthotic is running in the system tray.",
        "welcome_title": "Welcome to Synthotic",
        "welcome_head": "Privacy & Local Intelligence",
        "welcome_body": (
            "Thank you for installing Synthotic.\n\n"
            "This tool is designed for 100% privacy. "
            "All audio processing is performed on your hardware (CPU), "
            "sending no data to external clouds.\n\n"
            "On the first run, the AI will perform a one-time model download."
        ),
        "welcome_dev": "Developed by:",
        "welcome_btn": "GET STARTED",
        "about_desc": "Autonomous Meeting Recorder & Transcriber.\nPrivacy-First Local Processing.",
        "err_loopback_title": "Audio Device Not Found",
        "err_loopback_msg": "No system audio loopback device found.\n\nTo record system audio, enable a system-audio capture source (for example Stereo Mix on Windows or a PulseAudio/PipeWire monitor on Linux).\n\nWould you like to open the sound settings now?",
        "err_ffmpeg_title": "Audio Engine Error",
        "err_ffmpeg_msg": "Failed to start audio recording engine. Please verify that FFmpeg is installed correctly.",
        "settings_title": "Settings",
        "settings_audio": "Audio Devices",
        "settings_loopback": "System Audio (Loopback):",
        "settings_mic": "Microphone:",
        "settings_refresh": "Refresh Devices",
        "settings_folder": "Output Folder",
        "settings_folder_label": "Save Recordings to:",
        "settings_browse": "Browse...",
        "settings_save": "Save",
        "settings_cancel": "Cancel",
        "settings_auto_detect": "(Auto Detect)",
        "onboarding_welcome_title": "Welcome to Synthotic",
        "onboarding_welcome_desc": "Configure Synthotic in 3 quick steps to start transcribing meetings with total privacy.",
        "onboarding_folder_title": "Where to save recordings?",
        "onboarding_folder_desc": "Choose the folder where audio files and transcriptions will be saved.",
        "onboarding_devices_title": "Select Audio Devices",
        "onboarding_devices_desc": "Choose your system audio and microphone. Both are required.",
        "onboarding_confirm_title": "Confirm Settings",
        "onboarding_confirm_desc": "Review your choices before starting:",
        "onboarding_btn_next": "Next",
        "onboarding_btn_back": "Back",
        "onboarding_btn_finish": "Start Synthotic",
        "onboarding_err_no_folder": "Please select a valid folder.",
        "onboarding_err_no_devices": "Please select both audio devices.",
        "language": "en_US"
    }
}

# --- AUTHORSHIP & SOCIAL METADATA ---
MY_LINKEDIN = "https://www.linkedin.com/in/josefernandocunha/"
MY_GITHUB = "https://github.com/josecunha0/synthotic"
WEBSITE_URL = "https://Synthotic.com"
DEV_NAME = "José Cunha"
COPYRIGHT = "Copyright (c) 2026 José Cunha"
