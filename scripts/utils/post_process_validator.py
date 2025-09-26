# scripts/utils/post_process_validator.py
# ---------------------------------------------------------------
"""
后处理验证器 - 检查AI翻译后的文本格式是否符合游戏要求

这个模块负责在AI翻译完成后，对翻译结果进行格式验证，
确保所有游戏特定的语法结构都被正确保留。
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# 导入国际化支持
try:
    from . import i18n
except ImportError:
    i18n = None


class ValidationLevel(Enum):
    """验证级别枚举"""
    INFO = "info"      # 信息性提示
    WARNING = "warning"  # 警告
    ERROR = "error"    # 错误


@dataclass
class ValidationResult:
    """验证结果数据类"""
    is_valid: bool
    level: ValidationLevel
    message: str
    details: Optional[str] = None
    line_number: Optional[int] = None
    text_sample: Optional[str] = None


@dataclass
class ValidationRule:
    """验证规则数据类"""
    name: str                    # 规则名称
    pattern: str                 # 正则表达式模式
    level: ValidationLevel       # 验证级别
    message: str                 # 错误消息
    check_function: str          # 检查函数类型 ("banned_chars", "format", 或自定义函数)
    capture_group: int = 1       # 捕获组索引（默认为1）


class BaseGameValidator:
    """游戏验证器基类 (重构后)"""
    
    def __init__(self, game_id: str, game_name: str):
        self.game_id = game_id
        self.game_name = game_name
        self.logger = logging.getLogger(__name__)
        # 子类需要定义这个rules列表
        self.rules = self._get_rules()

    def _get_rules(self) -> List[ValidationRule]:
        """子类应该重写这个方法来提供自己的规则列表"""
        return []

    def _check_pattern_for_banned_chars(self, text: str, pattern: str, message: str, 
                                       level: ValidationLevel, line_number: Optional[int], 
                                       capture_group: int = 1) -> List[ValidationResult]:
        """
        一个可复用的检查器：查找一个模式，并检查其捕获组内是否包含不允许的非ASCII字符。
        这是一个可以被所有子类共享的"工人"方法。
        """
        results = []
        try:
            # 使用re.finditer以获取更详细的匹配对象信息
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) >= capture_group:
                    content = match.group(capture_group)
                    
                    # 查找所有非ASCII字符
                    banned_chars = re.findall(r'[^\x00-\x7F]', content)
                    
                    if banned_chars:
                        # 将找到的违规字符列表转换为去重的字符串，便于展示
                        details_str = "".join(sorted(list(set(banned_chars))))
                        
                        # 尝试使用国际化消息
                        try:
                            if i18n and i18n._language_loaded:
                                details_message = i18n.t("validation_generic_banned_chars_found", 
                                                       match_text=match.group(0), 
                                                       banned_chars=details_str)
                            else:
                                details_message = f"在 '{match.group(0)}' 中发现违规字符: '{details_str}'"
                        except:
                            details_message = f"在 '{match.group(0)}' 中发现违规字符: '{details_str}'"
                        
                        results.append(ValidationResult(
                            is_valid=False,
                            level=level,
                            message=message,
                            details=details_message,
                            line_number=line_number,
                            text_sample=text[:100] + "..." if len(text) > 100 else text
                        ))
        except Exception as e:
            self.logger.warning(f"规则检查失败: {e}，模式: {pattern}")
        
        return results

    def _check_pattern_format(self, text: str, pattern: str, message: str,
                             level: ValidationLevel, line_number: Optional[int],
                             format_regex: str) -> List[ValidationResult]:
        """
        检查模式格式是否符合预期格式
        """
        results = []
        try:
            matches = re.findall(pattern, text)
            for content in matches:
                if isinstance(content, tuple):
                    content = content[0] if content else ""
                
                if not re.match(format_regex, content):
                    results.append(ValidationResult(
                        is_valid=False,
                        level=level,
                        message=message,
                        details=self._get_i18n_message("validation_generic_format_error", content=content),
                        line_number=line_number,
                        text_sample=text[:100] + "..." if len(text) > 100 else text
                    ))
        except Exception as e:
            self.logger.warning(f"格式检查失败: {e}")
        
        return results

    def validate_text(self, text: str, line_number: Optional[int] = None) -> List[ValidationResult]:
        """
        现在这个方法是通用的！它会遍历子类定义的规则并执行它们。
        """
        all_results = []
        
        for rule in self.rules:
            try:
                # 根据规则类型调用相应的检查方法
                if rule.check_function == "banned_chars":
                    results = self._check_pattern_for_banned_chars(
                        text, rule.pattern, rule.message, rule.level, line_number, rule.capture_group
                    )
                elif rule.check_function == "format":
                    # 对于格式检查，需要额外的格式正则表达式
                    format_regex = getattr(rule, 'format_regex', r'^[A-Za-z_][A-Za-z0-9_]*$')
                    results = self._check_pattern_format(
                        text, rule.pattern, rule.message, rule.level, line_number, format_regex
                    )
                else:
                    # 自定义检查函数
                    results = rule.check_function(self, text, line_number)
                
                all_results.extend(results)
                
            except Exception as e:
                self.logger.error(f"执行规则 '{rule.name}' 时发生错误: {e}")
                continue
        
        # 子类可以添加一些无法用通用方法处理的、独特的检查逻辑
        custom_results = self._run_custom_checks(text, line_number)
        all_results.extend(custom_results)
        
        return all_results

    def _run_custom_checks(self, text: str, line_number: Optional[int]) -> List[ValidationResult]:
        """子类可以重写这个方法来添加自定义检查逻辑"""
        return []

    def _get_i18n_message(self, message_key: str, **kwargs) -> str:
        """获取国际化消息，如果失败则返回英文"""
        try:
            if i18n and i18n._language_loaded:
                return i18n.t(message_key, **kwargs)
            else:
                # 回退到英文
                return self._get_fallback_message(message_key, **kwargs)
        except:
            return self._get_fallback_message(message_key, **kwargs)
    
    def _get_fallback_message(self, message_key: str, **kwargs) -> str:
        """获取回退消息（英文）"""
        fallback_messages = {
            "validation_vic3_simple_concept_chinese": "Non-ASCII characters found in simple `[concept]` links.",
            "validation_vic3_concept_key_chinese": "Non-ASCII characters found in the 'key' part of `[Concept('key', ...)]` function. The 'key' must be in English.",
            "validation_vic3_scope_key_chinese": "Non-ASCII characters found in the 'key' part of `[SCOPE.sType('key')]` function. The 'key' must be in English.",
            "validation_vic3_icon_key_chinese": "Non-ASCII characters found in the 'key' part of icon tag `@key!`.",
            "validation_vic3_formatting_missing_space": "Formatting command `#{key}` is missing a required space after it.",
            "validation_vic3_unknown_formatting": "Unknown formatting command `#{key}`.",
            "validation_vic3_tooltippable_chinese": "Non-ASCII characters found in the 'key' part of `#tooltippable`. The key must be in English.",
            "validation_vic3_formatting_found_at": "Found at: '{found_text}', should be followed by a space.",
            "validation_vic3_unsupported_formatting": "Victoria 3 does not support the formatting command: '{found_text}'.",
            "validation_vic3_tooltippable_found_in": "Found banned characters '{banned_chars}' in '<{key_content}>'",
            "validation_stellaris_brackets_chinese": "Non-ASCII characters found in square brackets `[...]`. This is usually a translation error and may cause the game to fail to recognize commands.",
            "validation_stellaris_dollar_vars_chinese": "Non-ASCII characters found in dollar sign `$...$` variables. Variable names must retain their original text.",
            "validation_stellaris_pound_icons_chinese": "Non-ASCII characters found in pound sign `£...£` icon tags. Icon names must retain their original text.",
            "validation_stellaris_color_tags_mismatch": "Color tag `§...` and end marker `§!` count mismatch, which may cause text display anomalies.",
            "validation_stellaris_color_tags_count": "Found {start_count} start tags, but {end_count} end markers.",
            "validation_eu4_brackets_chinese": "Non-ASCII characters found in square bracket `[...]` commands.",
            "validation_eu4_legacy_vars_chinese": "Non-ASCII characters found in traditional `$KEY$` variables.",
            "validation_eu4_pound_icons_chinese": "Non-ASCII characters found in icon tags `£key£`.",
            "validation_eu4_country_flags_chinese": "Non-ASCII characters found in country flag tags `@TAG`.",
            "validation_eu4_color_tags_mismatch": "Color tag `§...` and end marker `§!` count mismatch, which may cause text display anomalies.",
            "validation_eu4_currency_symbol_detected": "Special currency symbol `¤` detected.",
            "validation_eu4_currency_symbol_note": "Ensure this symbol is properly preserved.",
            "validation_hoi4_namespaces_chinese": "Non-ASCII characters found in namespace `[Scope.Function]`, which may cause game crashes.",
            "validation_hoi4_formatting_vars_chinese": "Non-ASCII characters found in the variable part of formatting variables `[?variable|...]`.",
            "validation_hoi4_nested_strings_chinese": "Non-ASCII characters found in nested strings or variables `$key$`.",
            "validation_hoi4_icon_tags_chinese": "Non-ASCII characters found in icon tags `£icon_name`.",
            "validation_hoi4_country_flags_chinese": "Non-ASCII characters found in country flag tags `@TAG`.",
            "validation_hoi4_localization_formatters_chinese": "Non-ASCII characters found in standalone `formatter|token` formatters.",
            "validation_hoi4_color_tags_mismatch": "Color tag `§...` and end marker `§!` count mismatch, which may cause text display anomalies.",
            "validation_ck3_scopes_functions_chinese": "Non-ASCII characters found in square bracket `[...]` commands.",
            "validation_ck3_concept_key_chinese": "Non-ASCII characters found in the 'key' part of `[Concept('key', ...)]` function. The 'key' must be in English.",
            "validation_ck3_trait_title_key_chinese": "Non-ASCII characters found in the 'key' part of `GetTrait` or `GetTitleByKey` functions.",
            "validation_ck3_dollar_vars_chinese": "Non-ASCII characters found in dollar sign `$key$` variables.",
            "validation_ck3_icon_key_chinese": "Non-ASCII characters found in the 'key' part of icon tags `@key!`.",
            "validation_ck3_formatting_tags_mismatch": "Formatting command start tag `#key` and end marker `#!` count mismatch.",
            "validation_ck3_formatting_missing_space": "Formatting command `#{key}` may be missing a required space after it.",
            "validation_ck3_unknown_formatting": "Unknown formatting command `#{key}`.",
            "validation_ck3_formatting_found_at": "Found at: '{found_text}'",
            "validation_ck3_unsupported_formatting": "CK3 does not support the formatting command: '{found_text}'.",
            "validation_generic_banned_chars_found": "Found banned characters '{banned_chars}' in '{match_text}'",
            "validation_generic_format_error": "Format error: '{content}'",
            "validation_generic_color_tags_count": "Found {start_count} start tags, but {end_count} end markers."
        }
        
        message = fallback_messages.get(message_key, f"Unknown validation message: {message_key}")
        if kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
        return message

    def _log_validation_result(self, result: ValidationResult, text: str):
        """记录验证结果到日志"""
        # 尝试使用国际化消息
        try:
            if i18n and i18n._language_loaded:
                if result.level == ValidationLevel.ERROR:
                    self.logger.error(f"[{self.game_name}] {result.message}")
                    if result.details:
                        self.logger.error(f"{i18n.t('validation_details')}: {result.details}")
                elif result.level == ValidationLevel.WARNING:
                    self.logger.warning(f"[{self.game_name}] {result.message}")
                    if result.details:
                        self.logger.warning(f"{i18n.t('validation_details')}: {result.details}")
                else:
                    self.logger.info(f"[{self.game_name}] {result.message}")
            else:
                # 回退到英文
                if result.level == ValidationLevel.ERROR:
                    self.logger.error(f"[{self.game_name}] {result.message}")
                    if result.details:
                        self.logger.error(f"Details: {result.details}")
                elif result.level == ValidationLevel.WARNING:
                    self.logger.warning(f"[{self.game_name}] {result.message}")
                    if result.details:
                        self.logger.warning(f"Details: {result.details}")
                else:
                    self.logger.info(f"[{self.game_name}] {result.message}")
        except Exception as e:
            # 如果国际化失败，使用原始消息
            if result.level == ValidationLevel.ERROR:
                self.logger.error(f"[{self.game_name}] {result.message}")
                if result.details:
                    self.logger.error(f"Details: {result.details}")
            elif result.level == ValidationLevel.WARNING:
                self.logger.warning(f"[{self.game_name}] {result.message}")
                if result.details:
                    self.logger.warning(f"Details: {result.details}")
            else:
                self.logger.info(f"[{self.game_name}] {result.message}")


class Victoria3Validator(BaseGameValidator):
    """维多利亚3格式验证器 (重构后)"""
    
    def __init__(self):
        super().__init__("1", "Victoria 3")
        
    def _get_rules(self) -> List[ValidationRule]:
        """
        只在这里定义Victoria 3的规则列表。
        """
        return [
            ValidationRule(
                name="non_ascii_in_simple_concept",
                # 匹配简单的概念链接，如 [concept_legitimacy]
                # 避免与 [Concept('...')] 和 [SCOPE.sType('...')] 重叠
                pattern=r'\[(?!Concept\()(?!SCOPE\.[a-zA-Z]+\()([^\]]+)\]'
                ,
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_vic3_simple_concept_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_concept_key",
                # 匹配 [Concept('key', 'text')] 中的 'key' 部分
                pattern=r"\[Concept\('([^']+)',",
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_vic3_concept_key_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_scope_key",
                # 匹配 [SCOPE.sCountry('scope_name')...] 中的 'scope_name' 部分
                pattern=r"\[SCOPE\.[a-zA-Z]+\('([^']+)'\)",
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_vic3_scope_key_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_icon_key",
                # 匹配 @icon_name! 中的 icon_name 部分
                pattern=r'@([^!]+)!',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_vic3_icon_key_chinese"),
                check_function="banned_chars",
                capture_group=1
            )
        ]

    def _run_custom_checks(self, text: str, line_number: Optional[int]) -> List[ValidationResult]:
        """Victoria 3特有的自定义检查逻辑。"""
        results = []

        # 规则 1: 检查格式化命令 #key 后面是否缺少了必要的空格
        # 硬编码所有合法的格式化命令
        VALID_FORMATTING_KEYS = {
            # 来自 VIC3textformatting.gui 的全部 name
            'active', 'inactive', 'shadow',
            'white', 'darker_white', 'grey',
            'red', 'green', 'light_green', 'yellow', 'blue', 'U',
            'gold', 'O', 'black', 'bold_black',
            'default_text',
            'clickable_link', 'clickable_link_hover',
            'variable', 'V',
            'header', 'h1', 'title',
            'clickable',
            'negative_value', 'N', 'positive_value', 'P', 'zero_value', 'Z',
            'R', 'G', 'Y',
            'blue_value', 'gold_value',
            'concept', 'tooltippable_concept',
            'instruction', 'I',
            'lore',
            'tooltip_header', 'T', 'tooltip_sub_header', 'S',
            'tooltippable', 'tooltippable_name', 'tooltippable_no_shadow',
            'b',
            'maximum', 'outliner_header', 'regular_size',
            'todo', 'todo_in_tooltip', 'broken',
            # 兼容此前文档中提到的其它常见键（若引擎支持）
            'r', 'white', 'default_text', 'gray',
            'italic', 'l', 'L',
            # 实际生效但未文档化的命令（来自modder实践）
            'bold',    # 粗体文本，实际生效
            'v',       # 变量显示，实际生效
            'tooltip'  # 工具提示，实际生效
            'g'        # 按照岛岛说的，来自原版，实际生效    
        }
        # 不需要空格的命令（紧随分号等结构）
        NO_SPACE_REQUIRED_KEYS = {'tooltippable', 'tooltip'}
        
        # 查找所有 #key 格式的起始标签
        formatting_pattern = r'#([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.finditer(formatting_pattern, text)
        
        for match in matches:
            key = match.group(1)
            key_lower = key.lower()  # 转换为小写进行匹配
            
            # 合法命令：检查缺少空格
            if key_lower in VALID_FORMATTING_KEYS:
                if key_lower in NO_SPACE_REQUIRED_KEYS:
                    continue
                next_char_pos = match.end()
                if (
                    next_char_pos < len(text)
                    and text[next_char_pos] != ' '
                    and not text[next_char_pos:].strip().startswith('#!')
                ):
                    results.append(ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.WARNING,
                        message=self._get_i18n_message("validation_vic3_formatting_missing_space", key=key),
                        details=self._get_i18n_message("validation_vic3_formatting_found_at", found_text=match.group(0)),
                        line_number=line_number,
                        text_sample=text[:100] + "..." if len(text) > 100 else text
                    ))
            # 非法命令：直接报错
            else:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=self._get_i18n_message("validation_vic3_unknown_formatting", key=key),
                    details=self._get_i18n_message("validation_vic3_unsupported_formatting", found_text=match.group(0)),
                    line_number=line_number,
                    text_sample=text[:100] + "..." if len(text) > 100 else text
                ))

        # 规则 2: 检查 #tooltippable 的复杂结构中，key部分是否包含非ASCII字符
        tooltip_pattern = r'#tooltippable;tooltip:<([^>]+)>'
        tooltip_matches = re.finditer(tooltip_pattern, text)
        for match in tooltip_matches:
            key_content = match.group(1)
            banned_chars = re.findall(r'[^\x00-\x7F]', key_content)
            if banned_chars:
                details_str = "".join(sorted(list(set(banned_chars))))
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=self._get_i18n_message("validation_vic3_tooltippable_chinese"),
                    details=self._get_i18n_message("validation_vic3_tooltippable_found_in", key_content=key_content, banned_chars=details_str),
                    line_number=line_number,
                    text_sample=text[:100] + "..." if len(text) > 100 else text
                ))
            
        return results


class StellarisValidator(BaseGameValidator):
    """群星格式验证器 (重构后)"""
    
    def __init__(self):
        super().__init__("2", "Stellaris")
        
    def _get_rules(self) -> List[ValidationRule]:
        """
        只在这里定义Stellaris的规则列表。
        """
        return [
            ValidationRule(
                name="non_ascii_in_brackets",
                # 匹配并捕获 [...] 中的内容
                pattern=r'\[([^\]]+)\]',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_stellaris_brackets_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_dollar_vars",
                # 匹配并捕获 $...$ 中的内容，排除空格
                pattern=r'\$([^$\s]+)\$',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_stellaris_dollar_vars_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_pound_icons",
                # 匹配并捕获 £...£ 中的内容，排除空格
                pattern=r'£([^£\s]+)£',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_stellaris_pound_icons_chinese"),
                check_function="banned_chars",
                capture_group=1
            )
        ]

    def _run_custom_checks(self, text: str, line_number: Optional[int]) -> List[ValidationResult]:
        """Stellaris特有的自定义检查逻辑，用于检查不成对的颜色标签。"""
        results = []
        
        # 查找所有 § 后面跟着一个字母或数字的起始标签
        start_tags = re.findall(r'§[a-zA-Z0-9]', text)
        # 查找所有 §! 结束标签
        end_tags_count = text.count('§!')
        
        if len(start_tags) != end_tags_count:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=self._get_i18n_message("validation_stellaris_color_tags_mismatch"),
                details=self._get_i18n_message("validation_stellaris_color_tags_count", start_count=len(start_tags), end_count=end_tags_count),
                line_number=line_number,
                text_sample=text[:100] + "..." if len(text) > 100 else text
            ))
            
        return results

class EU4Validator(BaseGameValidator):
    """欧陆风云4格式验证器 (重构后)"""
    
    def __init__(self):
        super().__init__("3", "Europa Universalis IV")
        
    def _get_rules(self) -> List[ValidationRule]:
        """
        只在这里定义EU4的规则列表。
        """
        return [
            ValidationRule(
                name="non_ascii_in_brackets",
                # 匹配 [Scope.Function]
                pattern=r'\[([^\]]+)\]',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_eu4_brackets_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_legacy_vars",
                # 匹配 $KEY$ - 放宽限制以包含更多变量格式
                pattern=r'\$([^$\n]+)\$',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_eu4_legacy_vars_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_pound_icons",
                # 匹配 £key£
                pattern=r'£([^£\n]+)£',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_eu4_pound_icons_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_country_flags",
                # 匹配 @TAG - 放宽限制以包含更多格式
                pattern=r'@([^\s]+)',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_eu4_country_flags_chinese"),
                check_function="banned_chars",
                capture_group=1
            )
        ]

    def _run_custom_checks(self, text: str, line_number: Optional[int]) -> List[ValidationResult]:
        """EU4特有的自定义检查逻辑。"""
        results = []

        # 规则 1: 检查不成对的颜色标签 §...§!
        # 查找所有 § 后面跟着一个字母或数字的起始标签
        # 修复：使用更宽松的模式来匹配颜色标签
        start_tags = re.findall(r'§[a-zA-Z0-9]', text)
        # 查找所有 §! 结束标签
        end_tags_count = text.count('§!')
        
        if len(start_tags) != end_tags_count:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=self._get_i18n_message("validation_eu4_color_tags_mismatch"),
                details=self._get_i18n_message("validation_generic_color_tags_count", start_count=len(start_tags), end_count=end_tags_count),
                line_number=line_number,
                text_sample=text[:100] + "..." if len(text) > 100 else text
            ))

        # 规则 2: 检查特殊金币符号 ¤ 是否存在（信息性）
        if '¤' in text:
            results.append(ValidationResult(
                is_valid=True,  # 这不是一个错误，只是一个提示
                level=ValidationLevel.INFO,
                message=self._get_i18n_message("validation_eu4_currency_symbol_detected"),
                details=self._get_i18n_message("validation_eu4_currency_symbol_note"),
                line_number=line_number,
                text_sample=text[:100] + "..." if len(text) > 100 else text
            ))
            
        return results


class HOI4Validator(BaseGameValidator):
    """钢铁雄心4格式验证器 (重构后)"""

    def __init__(self):
        super().__init__("4", "Hearts of Iron IV")

    def _get_rules(self) -> List[ValidationRule]:
        """
        只在这里定义HOI4的规则列表。
        """
        return [
            ValidationRule(
                name="non_ascii_in_namespaces",
                # 匹配 [Scope.Function] 这种用法，但不包括 [?variable|...] 格式
                pattern=r'\[(?!\?)([^\]]+)\]',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_hoi4_namespaces_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_formatting_vars",
                # 匹配 [?variable|...] 中的 variable 部分
                pattern=r'\[\?([^|\]]+)',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_hoi4_formatting_vars_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_nested_strings",
                # 匹配 $key$ 或 $VARIABLE$
                pattern=r'\$([^$\n]+)\$',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_hoi4_nested_strings_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_icon_tags",
                # 匹配 £icon_name，包括可能包含中文的情况
                pattern=r'£([^$\s]+)',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_hoi4_icon_tags_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_country_flags",
                # 匹配 @TAG，包括可能包含中文的情况
                pattern=r'@([^\s]+)',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_hoi4_country_flags_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_localization_formatters",
                # 匹配独立的 formatter|token，不包括在方括号内的内容
                pattern=r'(?<!\[)([^|\s]+\|[^|\s]+)(?!\])',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_hoi4_localization_formatters_chinese"),
                check_function="banned_chars",
                capture_group=1
            )
        ]

    def _run_custom_checks(self, text: str, line_number: Optional[int]) -> List[ValidationResult]:
        """HOI4特有的自定义检查逻辑。"""
        results = []

        # 规则 1: 检查不成对的颜色标签 §...§!
        # 查找所有 § 后面跟着一个字母或数字的起始标签
        start_tags = re.findall(r'§[a-zA-Z0-9]', text)
        # 查找所有 §! 结束标签
        end_tags_count = text.count('§!')
        
        if len(start_tags) != end_tags_count:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=self._get_i18n_message("validation_hoi4_color_tags_mismatch"),
                details=self._get_i18n_message("validation_generic_color_tags_count", start_count=len(start_tags), end_count=end_tags_count),
                line_number=line_number,
                text_sample=text[:100] + "..." if len(text) > 100 else text
            ))
            
        return results


class CK3Validator(BaseGameValidator):
    """十字军之王3格式验证器 (重构后)"""
    
    def __init__(self):
        super().__init__("5", "Crusader Kings III")
        
    def _get_rules(self) -> List[ValidationRule]:
        """
        只在这里定义CK3的规则列表。
        """
        return [
            ValidationRule(
                name="non_ascii_in_scopes_and_functions",
                # 匹配 [...] 内部的作用域和函数名，但不包括带参数的复杂函数
                # 排除已经被其他规则处理的复杂函数，避免重叠
                pattern=r'\[(?!Concept\()(?!GetTrait\()(?!GetTitleByKey\()(?!GetFullName\|)([^\]]+)\]',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_ck3_scopes_functions_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_concept_key",
                # 匹配 [Concept('key', 'text')] 中的 'key' 部分
                pattern=r"\[Concept\('([^']+)',",
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_ck3_concept_key_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_trait_or_title_key",
                # 匹配 GetTrait('key') 或 GetTitleByKey('key') 中的 'key'
                pattern=r"\[(?:GetTrait|GetTitleByKey)\('([^']+)'\)",
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_ck3_trait_title_key_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_dollar_vars",
                # 匹配 $key$
                pattern=r'\$([^$|\s]+)\$',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_ck3_dollar_vars_chinese"),
                check_function="banned_chars",
                capture_group=1
            ),
            ValidationRule(
                name="non_ascii_in_icon_key",
                # 匹配 @icon_name! 中的 icon_name 部分
                pattern=r'@([^!]+)!',
                level=ValidationLevel.ERROR,
                message=self._get_i18n_message("validation_ck3_icon_key_chinese"),
                check_function="banned_chars",
                capture_group=1
            )
        ]

    def _run_custom_checks(self, text: str, line_number: Optional[int]) -> List[ValidationResult]:
        """CK3特有的自定义检查逻辑。"""
        results = []

        # 硬编码所有合法的格式化命令
        VALID_FORMATTING_KEYS = {
            # 基础颜色和对比度
            'high', 'medium', 'low', 'weak', 'flavor', 'F',
            'light_background', 'light_background_underline',
            
            # 帮助和提示
            'help', 'help_light_background', 'instruction', 'I',
            
            # 警告和提醒
            'warning', 'X', 'XB', 'Xlight', 'ENC', 'alert_trial', 'alert_bold',
            
            # 数值相关
            'value', 'V', 'negative_value', 'positive_value', 'mixed_value', 'zero_value',
            'N', 'P', 'Z', 'M', 'positive_value_toast',
            
            # 按钮和链接
            'clickable', 'game_link', 'L', 'explanation_link', 'E', 'explanation_link_light_background', 'B',
            
            # 特殊格式
            'G', 'G_light',
            
            # 工具提示标题
            'tooltip_heading', 'T', 'tooltip_subheading', 'S', 'tooltip_heading_small', 'TS',
            
            # 调试和特殊用途
            'debug', 'D', 'variable', 'date', 'trigger_inactive',
            'difficulty_easy', 'difficulty_medium', 'difficulty_hard', 'difficulty_very_hard',
            'true_white', 'TUT', 'TUT_KW', 'same',
            
            # 强调和样式
            'emphasis', 'EMP', 'BOL', 'UND', 'DIE1', 'DIE2', 'DIE3',
            'BER', 'POE', 'SUCGLOW', 'flatulence',
            
            # 战争相关
            'defender_color', 'attacker_color',
            
            # 信用相关
            'credits_title', 'credits_header', 'credits_subheader', 'credits_entries',
            
            # 能力相关
            'aptitude_terrible', 'aptitude_poor', 'aptitude_average', 'aptitude_good', 'aptitude_excellent',
            
            # 阴谋相关
            'scheme_odds_abysmal', 'scheme_odds_low', 'scheme_odds_medium', 'scheme_odds_high', 'scheme_odds_excellent',
            
            # 基础格式化命令
            'bold', 'italic', 'underline', 'indent_newline'
        }
        
        # 先统计起止标签数量
        start_tags = re.findall(r'#([a-zA-Z0-9_;]+)', text)
        end_tags_count = text.count('#!')

        # 如果数量不匹配，则只给出配对不匹配的警告，避免与缺空格的警告重复
        if len(start_tags) != end_tags_count:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=self._get_i18n_message("validation_ck3_formatting_tags_mismatch"),
                details=self._get_i18n_message("validation_generic_color_tags_count", start_count=len(start_tags), end_count=end_tags_count),
                line_number=line_number,
                text_sample=text[:100] + "..." if len(text) > 100 else text
            ))
            return results

        # 数量匹配时，再检查 #key 后是否缺少空格（且不是紧跟 '!'/';'）
        missing_space_pattern = r'#([a-zA-Z0-9_;]+)(?!\s|!|;)'
        for match in re.finditer(missing_space_pattern, text):
            key = match.group(1)
            # 检查是否是合法的格式化命令
            if key in VALID_FORMATTING_KEYS:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.WARNING,
                    message=self._get_i18n_message("validation_ck3_formatting_missing_space", key=key),
                    details=self._get_i18n_message("validation_ck3_formatting_found_at", found_text=match.group(0)),
                    line_number=line_number,
                    text_sample=text[:100] + "..." if len(text) > 100 else text
                ))
            else:
                # 未知的格式化命令
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=self._get_i18n_message("validation_ck3_unknown_formatting", key=key),
                    details=self._get_i18n_message("validation_ck3_unsupported_formatting", found_text=match.group(0)),
                    line_number=line_number,
                    text_sample=text[:100] + "..." if len(text) > 100 else text
                ))

        return results


class PostProcessValidator:
    """后处理验证器主类"""
    
    def __init__(self):
        self.validators = {
            "1": Victoria3Validator(),
            "2": StellarisValidator(),
            "3": EU4Validator(),
            "4": HOI4Validator(),
            "5": CK3Validator()
        }
        self.logger = logging.getLogger(__name__)
        
        # 加载国际化
        if i18n and not i18n._language_loaded:
            try:
                i18n.load_language()
            except Exception as e:
                self.logger.warning(f"Failed to load internationalization: {e}")
    
    def validate_game_text(self, game_id: str, text: str, line_number: Optional[int] = None) -> List[ValidationResult]:
        """
        验证指定游戏的文本格式
        
        Args:
            game_id: 游戏ID (1-5)
            text: 要验证的文本
            line_number: 行号
            
        Returns:
            验证结果列表
        """
        if game_id not in self.validators:
            try:
                if i18n and i18n._language_loaded:
                    self.logger.error(i18n.t("validation_unknown_game", game_id=game_id))
                else:
                    self.logger.error(f"Unknown game ID: {game_id}")
            except:
                self.logger.error(f"Unknown game ID: {game_id}")
            return []
        
        validator = self.validators[game_id]
        results = validator.validate_text(text, line_number)
        
        # 记录所有验证结果
        for result in results:
            validator._log_validation_result(result, text)
        
        return results
    
    def validate_batch(self, game_id: str, texts: List[str], start_line: int = 1) -> Dict[int, List[ValidationResult]]:
        """
        批量验证文本
        
        Args:
            game_id: 游戏ID
            texts: 文本列表
            start_line: 起始行号
            
        Returns:
            行号到验证结果的映射
        """
        batch_results = {}
        
        for i, text in enumerate(texts):
            line_number = start_line + i
            results = self.validate_game_text(game_id, text, line_number)
            if results:
                batch_results[line_number] = results
        
        return batch_results
    
    def get_validation_summary(self, batch_results: Dict[int, List[ValidationResult]]) -> Dict[str, int]:
        """
        获取验证结果摘要
        
        Args:
            batch_results: 批量验证结果
            
        Returns:
            各级别验证结果的统计
        """
        summary = {
            "total_lines": len(batch_results),
            "errors": 0,
            "warnings": 0,
            "info": 0
        }
        
        for line_results in batch_results.values():
            for result in line_results:
                if result.level == ValidationLevel.ERROR:
                    summary["errors"] += 1
                elif result.level == ValidationLevel.WARNING:
                    summary["warnings"] += 1
                else:
                    summary["info"] += 1
        
        return summary
    
    def log_validation_summary(self, batch_results: Dict[int, List[ValidationResult]], game_name: str = ""):
        """记录验证结果摘要到日志"""
        summary = self.get_validation_summary(batch_results)
        
        try:
            if i18n and i18n._language_loaded:
                if summary["errors"] > 0:
                    self.logger.error(i18n.t("validation_summary_errors", game_name=game_name, errors=summary["errors"], warnings=summary["warnings"]))
                elif summary["warnings"] > 0:
                    self.logger.warning(i18n.t("validation_summary_warnings", game_name=game_name, warnings=summary["warnings"]))
                else:
                    self.logger.info(i18n.t("validation_summary_success", game_name=game_name))
            else:
                # 回退到英文
                if summary["errors"] > 0:
                    self.logger.error(f"Format validation completed - {game_name}: Found {summary['errors']} errors, {summary['warnings']} warnings")
                elif summary["warnings"] > 0:
                    self.logger.warning(f"Format validation completed - {game_name}: Found {summary['warnings']} warnings")
                else:
                    self.logger.info(f"Format validation completed - {game_name}: All text formats are correct")
        except Exception as e:
            # 如果国际化失败，使用英文
            if summary["errors"] > 0:
                self.logger.error(f"Format validation completed - {game_name}: Found {summary['errors']} errors, {summary['warnings']} warnings")
            elif summary["warnings"] > 0:
                self.logger.warning(f"Format validation completed - {game_name}: Found {summary['warnings']} warnings")
            else:
                self.logger.info(f"Format validation completed - {game_name}: All text formats are correct")


# 便捷函数
def validate_text(game_id: str, text: str, line_number: Optional[int] = None) -> List[ValidationResult]:
    """便捷函数：验证单个文本"""
    validator = PostProcessValidator()
    return validator.validate_game_text(game_id, text, line_number)


def validate_batch(game_id: str, texts: List[str], start_line: int = 1) -> Dict[int, List[ValidationResult]]:
    """便捷函数：批量验证文本"""
    validator = PostProcessValidator()
    return validator.validate_batch(game_id, texts, start_line)


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 测试V3验证器
    v3_validator = Victoria3Validator()
    test_text = "这是一个测试文本，包含[GetName]和#bold 粗体文本#!"
    results = v3_validator.validate_text(test_text, 1)
    
    print(f"测试文本: {test_text}")
    print(f"验证结果数量: {len(results)}")
    for result in results:
        print(f"- {result.level.value}: {result.message}")
