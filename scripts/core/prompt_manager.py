import logging
from scripts.app_settings import GAME_PROFILES
from scripts.core.config_manager import config_manager

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages system prompts and custom prompts.
    Handles retrieval (merging defaults with overrides) and saving.
    """

    @staticmethod
    def get_all_prompts():
        """
        Returns a dictionary containing prompt info for all games,
        plus the custom global prompt.
        """
        overrides = config_manager.get_value("prompt_overrides", {})
        custom_global = config_manager.get_value("custom_global_prompt", "")
        
        system_prompts = {}
        for game_id, profile in GAME_PROFILES.items():
            default_prompt = profile.get("prompt_template", "")
            current_prompt = overrides.get(game_id, default_prompt)
            
            system_prompts[game_id] = {
                "name": profile["name"],
                "default": default_prompt,
                "current": current_prompt,
                "is_overridden": game_id in overrides
            }
            
        return {
            "system_prompts": system_prompts,
            "custom_global_prompt": custom_global
        }

    @staticmethod
    def get_effective_prompt(game_id: str) -> str:
        """Returns the effective prompt for a game (override or default)."""
        overrides = config_manager.get_value("prompt_overrides", {})
        if game_id in overrides:
            return overrides[game_id]
        
        profile = GAME_PROFILES.get(game_id)
        return profile.get("prompt_template", "") if profile else ""

    @staticmethod
    def get_custom_global_prompt() -> str:
        return config_manager.get_value("custom_global_prompt", "")

    @staticmethod
    def save_system_prompt_override(game_id: str, new_prompt: str):
        """Saves an override for a system prompt."""
        if game_id not in GAME_PROFILES:
            raise ValueError(f"Invalid game_id: {game_id}")
            
        overrides = config_manager.get_value("prompt_overrides", {})
        overrides[game_id] = new_prompt
        config_manager.set_value("prompt_overrides", overrides)
        logger.info(f"Saved prompt override for {game_id}")

    @staticmethod
    def save_custom_global_prompt(new_prompt: str):
        """Saves the custom global prompt."""
        config_manager.set_value("custom_global_prompt", new_prompt)
        logger.info("Saved custom global prompt")

    @staticmethod
    def reset_prompts(game_id: str = None, reset_all: bool = False, reset_custom: bool = False):
        """Resets prompts to default."""
        if reset_custom:
            config_manager.set_value("custom_global_prompt", "")
            logger.info("Reset custom global prompt")
            
        if reset_all:
            config_manager.set_value("prompt_overrides", {})
            logger.info("Reset all system prompt overrides")
        elif game_id:
            overrides = config_manager.get_value("prompt_overrides", {})
            if game_id in overrides:
                del overrides[game_id]
                config_manager.set_value("prompt_overrides", overrides)
                logger.info(f"Reset prompt override for {game_id}")

prompt_manager = PromptManager()
