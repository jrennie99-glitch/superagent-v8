"""
Plugin System
Extensible architecture for custom tools
"""
from typing import Dict, List, Callable, Any
from abc import ABC, abstractmethod
import importlib
import inspect

class Plugin(ABC):
    """Base plugin class - all plugins must inherit from this"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return plugin description"""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict:
        """Execute plugin functionality"""
        pass

class PluginSystem:
    """Manage and execute plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register_plugin(self, plugin: Plugin) -> bool:
        """Register a new plugin"""
        try:
            name = plugin.get_name()
            if name in self.plugins:
                return False
            
            self.plugins[name] = plugin
            return True
        except Exception:
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Plugin:
        """Get plugin by name"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict]:
        """List all registered plugins"""
        return [
            {
                "name": plugin.get_name(),
                "description": plugin.get_description()
            }
            for plugin in self.plugins.values()
        ]
    
    async def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Dict:
        """Execute a plugin"""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return {
                "success": False,
                "error": f"Plugin not found: {plugin_name}"
            }
        
        try:
            result = await plugin.execute(*args, **kwargs)
            return {
                "success": True,
                "plugin": plugin_name,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "plugin": plugin_name,
                "error": str(e)
            }
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    async def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger all callbacks for a hook"""
        if hook_name not in self.hooks:
            return
        
        for callback in self.hooks[hook_name]:
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception:
                continue

# Example plugin
class ExamplePlugin(Plugin):
    """Example plugin implementation"""
    
    def get_name(self) -> str:
        return "example"
    
    def get_description(self) -> str:
        return "Example plugin for demonstration"
    
    async def execute(self, *args, **kwargs) -> Dict:
        return {
            "message": "Example plugin executed",
            "args": args,
            "kwargs": kwargs
        }
