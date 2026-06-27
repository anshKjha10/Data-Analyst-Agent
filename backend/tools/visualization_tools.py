import os
import matplotlib
matplotlib.use('Agg')          # non-interactive backend — safe to use from threads
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
from backend.tools.s3_uploader import is_s3_configured, upload_image_buffer_to_s3

# Apply a clean dark style for all charts
plt.style.use('dark_background')
sns.set_theme(style="darkgrid", palette="muted")


def plot_chart(df, chart_type, x_col=None, y_col=None, save_dir="reports", filename=None):
    """
    Generates a chart based on the type, saves it, and returns the filepath.
    Prevents blocking by closing plt figures and using file exports.
    """
    try:
        fig, ax = plt.subplots(figsize=(8, 5))

        if not filename:
            safe_x = str(x_col).replace(" ", "_") if x_col else ""
            safe_y = str(y_col).replace(" ", "_") if y_col else ""
            suffix = f"_{safe_x}" + (f"_vs_{safe_y}" if safe_y else "")
            filename = f"{chart_type.lower().replace(' ', '_')}{suffix}.png"

        save_path = os.path.join(save_dir, filename)

        if chart_type != "Heatmap" and (not x_col or x_col not in df.columns):
            plt.close(fig)
            return {"error": f"Column '{x_col}' not found in dataset."}

        if chart_type in ["Scatter Plot", "Line Chart"] and (not y_col or y_col not in df.columns):
            plt.close(fig)
            return {"error": f"Column '{y_col}' not found in dataset for two-variable plot."}

        if chart_type == "Histogram":
            sns.histplot(df[x_col], kde=True, ax=ax)

        elif chart_type == "Bar Chart":
            df[x_col].value_counts().head(10).plot(kind="bar", ax=ax)
            plt.xticks(rotation=45)

        elif chart_type == "Pie Chart":
            df[x_col].value_counts().head(5).plot(
                kind="pie",
                autopct="%1.1f%%",
                ax=ax
            )
            ax.set_ylabel("")

        elif chart_type == "Scatter Plot":
            sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax)

        elif chart_type == "Line Chart":
            sns.lineplot(data=df, x=x_col, y=y_col, ax=ax)

        elif chart_type == "Box Plot":
            sns.boxplot(data=df, x=x_col, ax=ax)

        elif chart_type == "Violin Plot":
            sns.violinplot(data=df, x=x_col, ax=ax)

        elif chart_type == "Count Plot":
            sns.countplot(data=df, x=x_col, ax=ax)
            plt.xticks(rotation=45)

        elif chart_type == "Heatmap":
            corr = df.corr(numeric_only=True)
            if corr.empty:
                plt.close(fig)
                return {"error": "No numeric columns available for Heatmap correlation."}
            sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)

        ax.set_title(f"{chart_type}" + (f": {x_col}" if x_col else "") + (f" vs {y_col}" if y_col else ""))
        plt.tight_layout()

        if is_s3_configured():
            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches='tight')
            plt.close(fig)
            s3_url = upload_image_buffer_to_s3(buf, filename, content_type="image/png")
            return {"saved_path": s3_url}
        else:
            os.makedirs(save_dir, exist_ok=True)
            plt.savefig(save_path)
            plt.close(fig)
            return {"saved_path": save_path}

    except Exception as e:
        if 'fig' in locals():
            plt.close(fig)
        return {"error": f"Failed to plot chart: {str(e)}"}

