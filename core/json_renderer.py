"""
JSON renderer module for generating the final webtoon JSON output
"""
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.panel import Panel
from models.speech_bubble import SpeechBubble

# Configure logging
logger = logging.getLogger(__name__)

class JSONRenderer:
    """
    Renders panels and speech bubbles into JSON format for webtoon display
    """
    
    def __init__(self):
        """Initialize the JSON renderer"""
        logger.info("JSONRenderer initialized")
        
    def render_webtoon(
        self, 
        panels: List[Panel], 
        title: str = "SketchDojo Webtoon", 
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Render a complete webtoon from panels into JSON
        
        Args:
            panels: List of Panel objects to render
            title: Title of the webtoon
            timestamp: Optional timestamp for the webtoon
            
        Returns:
            Dictionary containing the webtoon data in JSON format
        """
        logger.info(f"Rendering webtoon JSON with {len(panels)} panels")
        
        # Create the base JSON structure
        webtoon_data = {
            "title": title,
            "createdAt": timestamp or datetime.now().isoformat(),
            "panels": []
        }
        
        # Process each panel
        for panel in panels:
            panel_data = self._render_panel(panel)
            webtoon_data["panels"].append(panel_data)
        
        logger.info("JSON rendering completed")
        return webtoon_data
    
    def _render_panel(self, panel: Panel) -> Dict[str, Any]:
        """
        Render a single panel to JSON format
        
        Args:
            panel: Panel object to render
            
        Returns:
            Dictionary containing the panel data
        """
        # Get panel size and determine type
        panel_size = getattr(panel, 'size', 'full')
        panel_type = panel_size
        
        # Get panel style
        panel_style = getattr(panel, 'style', 'normal')
        
        # Get image path
        image_path = getattr(panel, 'image_path', None)
        if image_path:
            # Don't add leading slash if it's a full URL
            if not (image_path.startswith('http://') or image_path.startswith('https://')):
                # For relative paths, add a leading slash if it doesn't have one
                image_path = f"/{image_path}" if not image_path.startswith('/') else image_path
        
        # Create base panel data
        panel_data = {
            "id": str(panel.panel_id),
            "type": panel_type,
            "style": panel_style,
            "image": image_path
        }
        
        # Add speech bubbles if any
        speech_bubbles = getattr(panel, 'speech_bubbles', [])
        if speech_bubbles:
            panel_data["speechBubbles"] = self._render_speech_bubbles(panel)
        
        # Add caption if any
        caption = getattr(panel, 'caption', None)
        if caption:
            panel_data["caption"] = caption
        
        # Add sound effects if any
        effects = getattr(panel, 'effects', [])
        if effects:
            panel_data["soundEffects"] = self._render_effects(effects)
        
        return panel_data
    
    def _render_speech_bubbles(self, panel: Panel) -> List[Dict[str, Any]]:
        """
        Render speech bubbles for a panel
        
        Args:
            panel: Panel containing speech bubbles
            
        Returns:
            List of speech bubble dictionaries
        """
        bubbles = []
        
        # If panel has structured speech bubble objects
        speech_bubbles = getattr(panel, 'speech_bubbles', [])
        if speech_bubbles:
            for bubble in speech_bubbles:
                bubble_data = {
                    "type": getattr(bubble, 'style', 'normal'),
                    "content": getattr(bubble, 'text', ''),
                    "position": self._get_position_dict(bubble),
                    "tailPosition": getattr(bubble, 'tail_direction', 'bottom'),
                    "character": getattr(bubble, 'character', None)
                }
                bubbles.append(bubble_data)
        
        # If panel just has dialogue list without structured bubbles
        elif hasattr(panel, 'dialogue') and panel.dialogue:
            for i, dialogue_item in enumerate(panel.dialogue):
                if isinstance(dialogue_item, dict) and 'text' in dialogue_item and 'character' in dialogue_item:
                    character = dialogue_item['character']
                    text = dialogue_item['text']
                else:
                    # Simple string dialogue
                    character = f"character-{i+1}"
                    text = str(dialogue_item)
                
                # Simple top-to-bottom layout
                bubble_data = {
                    "type": "normal",
                    "content": text,
                    "position": {
                        "top": f"{10 + (i * 20)}%",
                        "left": f"{10 + (i * 5)}%"
                    },
                    "tailPosition": "bottom",
                    "character": character
                }
                bubbles.append(bubble_data)
        
        return bubbles
    
    def _render_effects(self, effects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Render special effects for a panel
        
        Args:
            effects: List of effect dictionaries
            
        Returns:
            List of effect dictionaries
        """
        rendered_effects = []
        
        for effect in effects:
            if isinstance(effect, str):
                # Simple string effect
                effect_data = {
                    "text": effect,
                    "position": {
                        "top": "50%",
                        "left": "50%"
                    }
                }
                rendered_effects.append(effect_data)
            elif isinstance(effect, dict):
                # Dictionary with position and text
                effect_data = {
                    "text": effect.get('text', ''),
                    "position": {
                        "top": effect.get('top', '50%'),
                        "left": effect.get('left', '50%')
                    }
                }
                rendered_effects.append(effect_data)
        
        return rendered_effects
    
    def _get_position_dict(self, bubble: SpeechBubble) -> Dict[str, str]:
        """
        Generate position dictionary for a speech bubble
        
        Args:
            bubble: SpeechBubble object with position information
            
        Returns:
            Dictionary containing position information
        """
        position_dict = {}
        
        position = getattr(bubble, 'position', None)
        if position:
            # Handle different position formats
            if isinstance(position, dict):
                position_dict = position
            elif isinstance(position, str):
                # Handle position as a string like "top-left"
                position_parts = position.split('-')
                
                if "top" in position_parts:
                    position_dict["top"] = "10%"
                if "bottom" in position_parts:
                    position_dict["bottom"] = "10%"
                if "left" in position_parts:
                    position_dict["left"] = "10%"
                if "right" in position_parts:
                    position_dict["right"] = "10%"
                if "center" in position_parts:
                    if "top" in position_parts or "bottom" in position_parts:
                        position_dict["left"] = "50%"
                    else:
                        position_dict["top"] = "50%"
                        
                # If just "center", center both horizontally and vertically
                if position == "center":
                    position_dict = {
                        "top": "50%",
                        "left": "50%"
                    }
        
        return position_dict 