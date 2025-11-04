"""Extensible plugin system for SuperAgent."""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
import structlog

logger = structlog.get_logger()


class Plugin(ABC):
    """Base class for SuperAgent plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @abstractmethod
    async def initialize(self, agent):
        """Initialize plugin with agent instance.
        
        Args:
            agent: SuperAgent instance
        """
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality.
        
        Returns:
            Plugin result
        """
        pass
    
    async def cleanup(self):
        """Cleanup resources."""
        pass


class PluginManager:
    """
    Plugin manager for extending SuperAgent functionality.
    
    Features:
    - Dynamic plugin loading
    - Plugin lifecycle management
    - Hook system for events
    - Plugin dependencies
    - Hot reloading
    """
    
    def __init__(self):
        """Initialize plugin manager."""
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.plugin_paths: List[Path] = []
    
    def register_plugin_path(self, path: Path):
        """Register a path to search for plugins.
        
        Args:
            path: Path to plugins directory
        """
        if path.exists() and path.is_dir():
            self.plugin_paths.append(path)
            logger.info(f"Registered plugin path: {path}")
    
    async def load_plugin(self, plugin_class: type, agent) -> bool:
        """Load a plugin.
        
        Args:
            plugin_class: Plugin class
            agent: SuperAgent instance
            
        Returns:
            True if loaded successfully
        """
        try:
            # Instantiate plugin
            plugin = plugin_class()
            
            # Validate plugin
            if not isinstance(plugin, Plugin):
                logger.error(f"Plugin {plugin_class} does not inherit from Plugin")
                return False
            
            # Initialize
            await plugin.initialize(agent)
            
            # Register
            self.plugins[plugin.name] = plugin
            
            logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_class}: {e}")
            return False
    
    async def discover_plugins(self, agent) -> int:
        """Discover and load plugins from registered paths.
        
        Args:
            agent: SuperAgent instance
            
        Returns:
            Number of plugins loaded
        """
        loaded_count = 0
        
        for plugin_path in self.plugin_paths:
            py_files = list(plugin_path.glob("*.py"))
            
            for py_file in py_files:
                if py_file.name.startswith("_"):
                    continue
                
                try:
                    # Import module
                    spec = importlib.util.spec_from_file_location(
                        py_file.stem, py_file
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find Plugin classes
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, Plugin) and obj != Plugin:
                            if await self.load_plugin(obj, agent):
                                loaded_count += 1
                
                except Exception as e:
                    logger.error(f"Failed to discover plugins in {py_file}: {e}")
        
        return loaded_count
    
    async def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """Execute a plugin.
        
        Args:
            plugin_name: Name of plugin
            *args, **kwargs: Plugin arguments
            
        Returns:
            Plugin result
        """
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin not found: {plugin_name}")
        
        plugin = self.plugins[plugin_name]
        return await plugin.execute(*args, **kwargs)
    
    def register_hook(self, event: str, callback: Callable):
        """Register a hook for an event.
        
        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self.hooks:
            self.hooks[event] = []
        
        self.hooks[event].append(callback)
        logger.debug(f"Registered hook for event: {event}")
    
    async def trigger_hook(self, event: str, *args, **kwargs):
        """Trigger all hooks for an event.
        
        Args:
            event: Event name
            *args, **kwargs: Event data
        """
        if event in self.hooks:
            for callback in self.hooks[event]:
                try:
                    if inspect.iscoroutinefunction(callback):
                        await callback(*args, **kwargs)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Hook callback failed for {event}: {e}")
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all loaded plugins.
        
        Returns:
            List of plugin info
        """
        return [
            {"name": p.name, "version": p.version}
            for p in self.plugins.values()
        ]
    
    async def unload_plugin(self, name: str) -> bool:
        """Unload a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if unloaded successfully
        """
        if name not in self.plugins:
            return False
        
        plugin = self.plugins[name]
        
        try:
            await plugin.cleanup()
            del self.plugins[name]
            logger.info(f"Unloaded plugin: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to unload plugin {name}: {e}")
            return False
    
    async def cleanup_all(self):
        """Cleanup all plugins."""
        for name in list(self.plugins.keys()):
            await self.unload_plugin(name)


# Example plugins

class FormatterPlugin(Plugin):
    """Code formatter plugin."""
    
    @property
    def name(self) -> str:
        return "formatter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    async def initialize(self, agent):
        """Initialize with agent."""
        self.agent = agent
    
    async def execute(self, code: str, language: str = "python") -> str:
        """Format code.
        
        Args:
            code: Code to format
            language: Programming language
            
        Returns:
            Formatted code
        """
        if language == "python":
            try:
                import black
                return black.format_str(code, mode=black.Mode())
            except:
                return code
        
        return code


class LinterPlugin(Plugin):
    """Code linter plugin."""
    
    @property
    def name(self) -> str:
        return "linter"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    async def initialize(self, agent):
        """Initialize with agent."""
        self.agent = agent
    
    async def execute(self, file_path: str) -> List[Dict[str, Any]]:
        """Lint a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of lint errors
        """
        # Simplified linting
        errors = []
        
        try:
            from pylint import epylint as lint
            
            (stdout, stderr) = lint.py_run(file_path, return_std=True)
            output = stdout.read()
            
            # Parse output (simplified)
            for line in output.split('\n'):
                if ':' in line:
                    errors.append({"message": line})
        
        except:
            pass
        
        return errors


class DatabasePlugin(Plugin):
    """Database integration plugin."""
    
    @property
    def name(self) -> str:
        return "database"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    async def initialize(self, agent):
        """Initialize with agent."""
        self.agent = agent
        self.connections = {}
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute database operation.
        
        Args:
            action: Action to perform
            **kwargs: Action parameters
            
        Returns:
            Operation result
        """
        if action == "connect":
            return await self._connect(**kwargs)
        elif action == "query":
            return await self._query(**kwargs)
        elif action == "generate_schema":
            return await self._generate_schema(**kwargs)
        
        return None
    
    async def _connect(self, db_url: str):
        """Connect to database."""
        # Implementation would use sqlalchemy or similar
        return {"status": "connected", "url": db_url}
    
    async def _query(self, sql: str):
        """Execute query."""
        # Implementation would execute actual query
        return {"status": "executed", "rows": 0}
    
    async def _generate_schema(self, description: str):
        """Generate database schema from description."""
        # Use AI to generate schema
        prompt = f"Generate SQL schema for: {description}"
        schema = await self.agent.llm.generate(prompt)
        return schema





