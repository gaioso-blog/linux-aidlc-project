"""Weekly report generation service."""
from collections import defaultdict

from aws_lambda_powertools import Logger

from src.models.task import Task
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository

logger = Logger(child=True)

# Maps user_id → email, used for report summary headers
UserMap = dict[str, str]


class ReportService:
    """Generates weekly progress reports from task data."""

    def __init__(
        self,
        task_repository: TaskRepository | None = None,
        user_repository: UserRepository | None = None,
    ) -> None:
        self._task_repo = task_repository or TaskRepository()
        self._user_repo = user_repository or UserRepository()

    def generate_weekly_report(self) -> str:
        """
        Aggregate all tasks and produce an HTML weekly report.

        Report sections:
        - Total backlog (all non-done tasks)
        - Tasks by status per user
        - Summary table
        """
        tasks = self._task_repo.list_all()
        users = self._user_repo.list_all()
        user_map: UserMap = {u.user_id: u.name for u in users}

        aggregated = self._aggregate_tasks(tasks, user_map)
        html = self._build_report_html(aggregated, total_tasks=len(tasks))
        return html

    def _aggregate_tasks(
        self, tasks: list[Task], user_map: UserMap
    ) -> dict:
        """
        Build an aggregation dict:
        {
            "by_user": { user_name: { "pending": [...], "in_progress": [...], "done": [...] } },
            "totals": { "pending": int, "in_progress": int, "done": int },
            "backlog_count": int,
        }
        """
        by_user: dict[str, dict[str, list[Task]]] = defaultdict(
            lambda: {"pending": [], "in_progress": [], "done": []}
        )
        totals: dict[str, int] = {"pending": 0, "in_progress": 0, "done": 0}

        for task in tasks:
            status = task.status
            if status in totals:
                totals[status] += 1

            user_label = user_map.get(task.assignee_id or "", "Não atribuído")
            if status in by_user[user_label]:
                by_user[user_label][status].append(task)

        backlog_count = totals.get("pending", 0) + totals.get("in_progress", 0)

        return {
            "by_user": dict(by_user),
            "totals": totals,
            "backlog_count": backlog_count,
        }

    def _build_report_html(self, aggregated: dict, total_tasks: int) -> str:
        """Render the aggregation into an HTML email body."""
        totals = aggregated["totals"]
        backlog = aggregated["backlog_count"]
        by_user = aggregated["by_user"]

        # User rows
        user_rows = ""
        for user_name, statuses in by_user.items():
            pending_count = len(statuses.get("pending", []))
            in_progress_count = len(statuses.get("in_progress", []))
            done_count = len(statuses.get("done", []))
            user_rows += f"""
            <tr>
                <td>{user_name}</td>
                <td style="text-align:center;">{pending_count}</td>
                <td style="text-align:center;">{in_progress_count}</td>
                <td style="text-align:center;">{done_count}</td>
            </tr>"""

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto;">
            <h2 style="color: #2c3e50;">Relatório Semanal — Task Manager</h2>

            <h3>Resumo Geral</h3>
            <table style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
                <tr style="background: #3498db; color: white;">
                    <th style="padding: 8px; text-align: left;">Métrica</th>
                    <th style="padding: 8px; text-align: center;">Qtd</th>
                </tr>
                <tr><td style="padding: 8px;">Total de tarefas</td>
                    <td style="padding: 8px; text-align: center;">{total_tasks}</td></tr>
                <tr style="background: #ecf0f1;"><td style="padding: 8px;">Backlog (pendente + em andamento)</td>
                    <td style="padding: 8px; text-align: center;">{backlog}</td></tr>
                <tr><td style="padding: 8px;">✅ Concluídas</td>
                    <td style="padding: 8px; text-align: center;">{totals.get("done", 0)}</td></tr>
                <tr style="background: #ecf0f1;"><td style="padding: 8px;">🔄 Em andamento</td>
                    <td style="padding: 8px; text-align: center;">{totals.get("in_progress", 0)}</td></tr>
                <tr><td style="padding: 8px;">⏳ Pendentes</td>
                    <td style="padding: 8px; text-align: center;">{totals.get("pending", 0)}</td></tr>
            </table>

            <h3>Por Membro da Equipe</h3>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="background: #2c3e50; color: white;">
                    <th style="padding: 8px; text-align: left;">Membro</th>
                    <th style="padding: 8px; text-align: center;">Pendente</th>
                    <th style="padding: 8px; text-align: center;">Em Andamento</th>
                    <th style="padding: 8px; text-align: center;">Concluído</th>
                </tr>
                {user_rows}
            </table>

            <hr style="margin-top: 30px;">
            <p style="color: #7f8c8d; font-size: 12px;">
                Relatório gerado automaticamente pelo Task Manager — Uso interno
            </p>
        </body>
        </html>
        """
