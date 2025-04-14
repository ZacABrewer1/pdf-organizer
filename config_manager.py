import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration and file mappings"""
    
    def __init__(self, config_folder: str = '.'):
        """
        Initialize with config folder
        
        Args:
            config_folder: Folder where configuration files will be stored
        """
        self.config_folder = config_folder
        self.mapping_file = os.path.join(config_folder, "pdf_mapping.json")
        self.config_file = os.path.join(config_folder, "pdf_organizer_config.json")
        
        # Create config folder if it doesn't exist
        os.makedirs(config_folder, exist_ok=True)
    
    def load_mapping(self) -> Dict[str, str]:
        """
        Load mapping from JSON file
        
        Returns:
            Dictionary mapping PDF filenames to target folders
        """
        if not os.path.exists(self.mapping_file):
            logger.info(f"Mapping file not found at {self.mapping_file}, creating new")
            return {}
            
        try:
            with open(self.mapping_file, 'r') as f:
                mapping = json.load(f)
                logger.info(f"Loaded {len(mapping)} mappings from {self.mapping_file}")
                return mapping
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in mapping file {self.mapping_file}")
            return {}
        except Exception as e:
            logger.error(f"Error loading mapping file: {e}")
            return {}
    
    def save_mapping(self, mapping: Dict[str, str]) -> bool:
        """
        Save mapping to JSON file
        
        Args:
            mapping: Dictionary mapping PDF filenames to target folders
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(mapping, f, indent=4)
                logger.info(f"Saved {len(mapping)} mappings to {self.mapping_file}")
                return True
        except Exception as e:
            logger.error(f"Error saving mapping file: {e}")
            return False
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        Returns:
            Dictionary containing configuration settings
        """
        default_config = {
            'target_folders': {},
            'patterns': [r"Job:\s*(.*)"],
            'is_move_operation': True,
            'recent_folders': []
        }
        
        if not os.path.exists(self.config_file):
            logger.info(f"Config file not found at {self.config_file}, using defaults")
            return default_config
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                
                # Update with any missing defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                        
                return config
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file {self.config_file}")
            return default_config
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return default_config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            config: Dictionary containing configuration settings
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
                logger.info(f"Saved configuration to {self.config_file}")
                return True
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            return False
    
    def update_recent_folder(self, folder_path: str):
        """
        Update recent folders list
        
        Args:
            folder_path: Path to add to recent folders
        """
        config = self.load_config()
        recent_folders = config.get('recent_folders', [])
        
        # Add to front if not already present, otherwise move to front
        if folder_path in recent_folders:
            recent_folders.remove(folder_path)
        
        # Add to front and limit to 10 items
        recent_folders.insert(0, folder_path)
        config['recent_folders'] = recent_folders[:10]
        
        self.save_config(config)
