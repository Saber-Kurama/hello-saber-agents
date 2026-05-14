"""Skill Tool - 技能工具

允许 Agent 按需加载领域知识。

特性：
- 渐进式披露：仅在需要时加载完整技能
- 缓存友好：作为 tool_result 注入，不修改 system_prompt
- 资源提示：自动列出可用的脚本、文档、示例等
- 参数替换：支持 $ARGUMENTS 占位符

使用示例：
    >>> from hello_agents.skills import SkillLoader
    >>> from hello_agents.tools.builtin.skill_tool import SkillTool
    >>> loader = SkillLoader(skills_dir=Path("skills"))
    >>> tool = SkillTool(skill_loader=loader)
    >>> # Agent 调用
    >>> response = tool.run({"skill": "pdf"})
"""

from typing import Any, Dict, List
from book_demo.tools.base import Tool, ToolParameter


class SkillTool(Tool):
    """Skill Tool - 技能工具"""
    def __init__(self):
        descriptions = self.get_metada_descriptions()
        super().__init__(
            name="Skill",
            description=f"""加载技能获取专业知识。

            可用技能：
            {descriptions}

            何时使用：
            - 任务明确匹配某个技能描述时，立即使用
            - 开始领域特定工作之前
            - 需要模型不具备的专业知识时

            注意：加载技能后，请严格遵循技能说明来完成用户任务。"""
                    )
    
    def run(self, parameters: Dict[str, Any]) -> str:
        """执行技能加载

        Args:
            parameters: 包含 skill 和可选 args 的参数字典

        Returns:
            ToolResponse: 包含完整技能内容的响应
        """
        skill_name = parameters.get("skill")
        skill_args = parameters.get("args")
        
        if not skill_name:
            return "错误：技能名称不能为空"

        try:
            print(f"获取技能内容: {skill_name}")
            print(f"获取技能参数: {skill_args}")
            skill_content = self.get_skill_content(skill_name)
            skill_content = skill_content.replace("$ARGUMENTS", skill_args or "")
            print(f"技能内容: {skill_content}")
            full_content = f"""<skill-loaded name="{skill_name}">
            {skill_content}
            </skill-loaded>"""    
            print(f"技能工具运行成功: {full_content}")
            return full_content
        except Exception as e:
            return f"错误：执行技能加载时发生异常: {str(e)}"



    def get_parameters(self) -> List[ToolParameter]:
        """获取工具参数"""
        return [
            ToolParameter(
                name="skill",
                type="string",
                description="要加载的技能名称",
                required=True
            ),
            ToolParameter(
                name="args",
                type="string",
                description="可选参数，将替换 SKILL.md 中的 $ARGUMENTS 占位符",
                required=False,
                default=""
            )
        ]

    def get_metada_descriptions(self) -> str:
        """获取技能描述"""
        return """
        - test-skill: A test skill for unit testing
        """

    def get_skill_content(self, skill_name: str) -> str:
        """获取技能内容"""
        return f"""
        
        # Test Skill

        This is a test skill body.

        ## Usage

        Use this skill for testing.

        $ARGUMENTS
        """