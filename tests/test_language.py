from os import environ
from src.core.language import BirbiaLanguage


def declare_environ():
    environ["ENV_IS_DEV"] = "True"
    environ["PREFIX"] = "birbia"
    environ["DEV_PREFIX"] = "birbia-beta"


def check_lang_entries(lang_code: str):
    lang = BirbiaLanguage.instance()
    lang.change_lang(lang_code)

    assert lang.LANG_CODE == lang_code

    # Normal entries
    assert lang.commands
    assert lang.version
    assert lang.title
    assert lang.original_title
    assert lang.categories
    assert lang.pages
    assert lang.timeout_warn
    assert lang.help_commands
    assert lang.cant_enter_vc
    assert lang.already_in_vc
    assert lang.no_vc
    assert lang.play_empty_query
    assert lang.play_fetching_query
    assert lang.play_platform_not_supported
    assert lang.play_failed_query
    assert lang.play_failed_error
    assert lang.play_ig_not_video
    assert lang.action_pause
    assert lang.action_pause_empty
    assert lang.action_resume
    assert lang.action_resume_empty
    assert lang.action_skip
    assert lang.action_skip_empty
    assert lang.action_clear
    assert lang.action_stop
    assert lang.queue_empty
    assert lang.queue_title
    assert lang.now_empty
    assert lang.now_title
    assert lang.invite_zero
    assert lang.invite_gen
    assert lang.purge_amount
    assert lang.purge_success
    assert lang.doujin_not_in_source
    assert lang.doujin_no_sauce
    assert lang.doujin_invalid_sauce
    assert lang.doujin_minimum
    assert lang.doujin_unknown_opt
    assert lang.ai_init_message

    # Help commands
    assert lang.help_commands["general"]
    assert lang.help_commands["music"]
    assert lang.help_commands["doujin"]

    # General commands
    assert lang.get_cmd_help("general", "description")
    assert lang.get_cmd_help("general", "help")
    assert lang.get_cmd_help("general", "music")
    assert lang.get_cmd_help("general", "doujin")

    # Music commands
    assert lang.get_cmd_help("music", "title")
    assert lang.get_cmd_help("music", "description")
    assert lang.get_cmd_help("music", "play")
    assert lang.get_cmd_help("music", "title")
    assert lang.get_cmd_help("music", "pause")
    assert lang.get_cmd_help("music", "resume")
    assert lang.get_cmd_help("music", "skip")
    assert lang.get_cmd_help("music", "queue")
    assert lang.get_cmd_help("music", "clear")
    assert lang.get_cmd_help("music", "leave")
    assert lang.get_cmd_help("music", "now")

    # Doujin commands
    assert lang.get_cmd_help("doujin", "title")
    assert lang.get_cmd_help("doujin", "description")
    assert lang.get_cmd_help("doujin", "description")
    assert lang.get_cmd_help("doujin", "doujin")
    assert lang.get_cmd_help("doujin", "arguments")
    assert lang.get_cmd_help("doujin", "arg_sauce")


def test_english_lang():
    declare_environ()
    check_lang_entries("en")


def test_spanish_lang():
    declare_environ()
    check_lang_entries("es")
