import os
import pkgutil
import importlib

def import_all_modules(package_name, exclude=None):
    """
    动态导入包及其子包的所有模块，支持排除指定模块。

    Args:
        package_name (str): 要导入的包名。
        exclude (list): 要排除的模块或包的全名列表（字符串），默认值为 None。
    """
    exclude = set(exclude or [])  # 转换为集合，方便高效检查
    package_dir = os.path.dirname(__file__)

    for _, module_name, is_pkg in pkgutil.walk_packages([package_dir], prefix=f"{package_name}."):
        # 跳过排除的模块
        if module_name in exclude:
            continue
        try:
            # 动态导入模块
            module = importlib.import_module(module_name)
            
            # 检查模块是否定义了 __all__
            if hasattr(module, '__all__'):
                globals().update({name: getattr(module, name) for name in module.__all__})
            else:
                globals().update({name: getattr(module, name) for name in dir(module) if not name.startswith("_")})
        except Exception as e:
            print(f"Failed to import {module_name}: {e}")

# 自动导入所有模块，示例中没有排除任何模块
# 可以通过传递 exclude 参数来控制排除特定模块
import_all_modules(__name__, exclude=['bill_parser.base'])
