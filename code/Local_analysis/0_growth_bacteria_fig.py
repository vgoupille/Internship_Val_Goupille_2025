# %%
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# set the working directory
os.chdir("/Users/valentingoupille/Documents/Rapport_stage")


# %%


# Lire le fichier sans en-tête
df = pd.read_excel("data/plan_exp.xlsx", sheet_name="suivi", header=None)

# Convertir les valeurs de la première ligne (sauf la première colonne) en datetime
df.iloc[0, 1:] = pd.to_datetime(df.iloc[0, 1:])

# Récupérer les timepoints depuis la première ligne
timepoints = df.iloc[0, 1:]

# Supprimer les deux premières lignes : [0] pour les dates, [1] pour les incubations
data = df.iloc[2:, :].copy()

# Renommer les colonnes : "Condition" + timepoints convertis en liste
data.columns = ["Condition"] + list(timepoints)

# Réinitialiser les index
data = data.reset_index(drop=True)

print(data)


# %%
# Passer au format long
data_long = data.melt(id_vars="Condition", var_name="Time", value_name="OD")

# Afficher le résultat
print(data_long)


# %%
start_time = pd.Timestamp("2025-03-13 09:45:00") - pd.Timedelta(hours=17, minutes=45)

# S'assurer que la colonne Time est bien en datetime
data_long["Time"] = pd.to_datetime(data_long["Time"])

# Calculer le temps d'incubation (différence en timedelta)
data_long["Incubation_timedelta"] = data_long["Time"] - start_time

# Optionnel : si tu souhaites uniquement des valeurs positives, sinon commenter cette ligne
data_long = data_long[data_long["Incubation_timedelta"] >= pd.Timedelta(0)]


# Formater en "XXhYY" (heures et minutes)
def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h{minutes:02d}"


data_long["Incubation_t"] = data_long["Incubation_timedelta"].apply(format_timedelta)

# Optionnel : supprimer la colonne temporaire timedelta si tu ne veux pas la garder
data_long.drop(columns=["Incubation_timedelta"], inplace=True)

print(data_long)


# %%
import pandas as pd

# 1. Lire le fichier contenant les ODt
odt_df = pd.read_excel("data/plan_exp.xlsx", sheet_name="ODt")


print(odt_df)
# S'assurer que 'Incubation_t' est bien au format string
odt_df["Incubation_t"] = odt_df["Incubation_t"].astype(str)

# 2. S'assurer que dans data_long aussi, c'est du texte
data_long["Incubation_t"] = data_long["Incubation_t"].astype(str)

# 3. Faire le merge
merged_df = pd.merge(
    data_long,
    odt_df[["Condition", "Incubation_t", "ODt"]],
    on=["Condition", "Incubation_t"],
    how="left",
).reindex(columns=list(data_long.columns) + ["ODt"])

print(merged_df)


# %%
# Group by Condition and get unique ODt values
merged_df.groupby("Condition")["ODt"].unique()


# %%


# Exemple de fonction pour convertir "XXhYY" en pd.Timedelta
def str_to_timedelta(s):
    try:
        h, m = s.split("h")
        return pd.Timedelta(hours=int(h), minutes=int(m))
    except Exception:
        return pd.NaT  # si la conversion échoue


# Appliquer la conversion à la colonne "Incubation_t"
merged_df["Incubation_timedelta"] = merged_df["Incubation_t"].apply(str_to_timedelta)

# Créer une colonne numérique en heures pour l'axe x
merged_df["Incubation_hours"] = (
    merged_df["Incubation_timedelta"].dt.total_seconds() / 3600
)

plt.figure(figsize=(12, 8))

# Tracer le graphique avec la colonne numérique et forcer l'axe x à commencer à 0
sns.lineplot(data=merged_df, x="Incubation_hours", y="OD", hue="Condition", marker="o")
plt.xlim(15, max(merged_df["Incubation_hours"]) + 3)  # Force x-axis to start at 0

# Add annotations for points with ODt values but only for M9_A and M9F_A conditions
for idx, row in merged_df[
    (~merged_df["ODt"].isna()) & (merged_df["Condition"].isin(["M9_A", "M9F_A"]))
].iterrows():
    # Set color based on condition
    label_color = "green" if row["Condition"].startswith("M9F") else "red"

    # Map OD values to sampling labels with condition prefix
    od_value = str(row["ODt"]).strip()
    condition_prefix = "M9F" if row["Condition"].startswith("M9F") else "M9"

    if od_value == "OD1":
        sampling_label = f"{condition_prefix} sampling_t1"
    elif od_value == "OD2":
        sampling_label = f"{condition_prefix} sampling_t2"
    elif od_value == "OD3":
        sampling_label = f"{condition_prefix} sampling_t3"
    else:
        sampling_label = str(row["ODt"])

    # Set annotation position
    if sampling_label == "M9 sampling_t1":
        y_pos = 0.03
        xytext = (5, 10)
    else:
        y_pos = row["OD"]
        xytext = (5, 5)

    # Format time as DD-MM HH:MM
    time_str = row["Time"].strftime("%d-%m %H:%M")
    plt.annotate(
        f"{sampling_label}\n{time_str}",
        xy=(row["Incubation_hours"], y_pos),
        xytext=xytext,
        textcoords="offset points",
        fontsize=8,
        color=label_color,
        bbox=dict(facecolor="white", edgecolor=label_color, alpha=0.7),
    )

plt.title("Evolution of OD over Time by Condition")
plt.xlabel("Incubation Time (hours)")
plt.ylabel("OD")
plt.legend(title="Condition", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()


# %%

import matplotlib.pyplot as plt
import seaborn as sns

# Create a time series plot showing OD evolution over time for each condition
plt.figure(figsize=(12, 8))  # Adjusted figure size to be more reasonable

# Plot the main lines
sns.lineplot(data=merged_df, x="Time", y="OD", hue="Condition", marker="o")

# Add labels for points with ODt values but only for M9_A and M9F_A conditions
for idx, row in merged_df[
    (~merged_df["ODt"].isna()) & (merged_df["Condition"].isin(["M9_A", "M9F_A"]))
].iterrows():
    # Format time as DD-MM HH:MM
    time_str = row["Time"].strftime("%d-%m %H:%M")

    # Set color based on condition
    label_color = "green" if row["Condition"].startswith("M9F") else "red"

    # Map OD values to sampling labels with condition prefix
    od_value = str(row["ODt"]).strip()
    condition_prefix = "M9F" if row["Condition"].startswith("M9F") else "M9"

    if od_value == "OD1":
        sampling_label = f"{condition_prefix} sampling_t1"
    elif od_value == "OD2":
        sampling_label = f"{condition_prefix} sampling_t2"
    elif od_value == "OD3":
        sampling_label = f"{condition_prefix} sampling_t3"
    else:
        sampling_label = str(row["ODt"])

    # Set annotation position
    if sampling_label == "M9 sampling_t1":
        y_pos = 0.01  # Fixed position at 0.01
        xytext = (5, 10)  # Offset from point
    else:
        y_pos = row["OD"]
        xytext = (5, 5)

    plt.annotate(
        f"{sampling_label}\n{time_str}",
        xy=(row["Time"], y_pos),
        xytext=xytext,
        textcoords="offset points",
        fontsize=8,
        color=label_color,
        bbox=dict(facecolor="white", edgecolor=label_color, alpha=0.7),
    )

plt.title("Evolution of OD over Time by Condition")
plt.xlabel("Time (DD-MM HH:MM)")
plt.ylabel("OD")
plt.legend(title="Condition", bbox_to_anchor=(1.05, 1), loc="upper left")

# Format x-axis ticks to show date and time
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%d-%m %H:%M"))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


import matplotlib.pyplot as plt
import seaborn as sns

# Create a time series plot showing OD evolution over time for each condition
plt.figure(figsize=(12, 8))  # Adjusted figure size to be more reasonable

# Plot the main lines
sns.lineplot(data=merged_df, x="Incubation_t", y="OD", hue="Condition", marker="o")

# Add labels for points with ODt values but only for M9_A and M9F_A conditions
for idx, row in merged_df[
    (~merged_df["ODt"].isna()) & (merged_df["Condition"].isin(["M9_A", "M9F_A"]))
].iterrows():
    # Set color based on condition
    label_color = "green" if row["Condition"].startswith("M9F") else "red"

    # Map OD values to sampling labels with condition prefix
    od_value = str(row["ODt"]).strip()
    condition_prefix = "M9F" if row["Condition"].startswith("M9F") else "M9"

    if od_value == "OD1":
        sampling_label = f"{condition_prefix} sampling_t1"
    elif od_value == "OD2":
        sampling_label = f"{condition_prefix} sampling_t2"
    elif od_value == "OD3":
        sampling_label = f"{condition_prefix} sampling_t3"
    else:
        sampling_label = str(row["ODt"])

    # Set annotation position
    if sampling_label == "M9 sampling_t1":
        y_pos = 0.01  # Fixed position at 0.01
        xytext = (5, 10)  # Offset from point
    else:
        y_pos = row["OD"]
        xytext = (5, 5)

    plt.annotate(
        f"{sampling_label}",
        xy=(row["Incubation_t"], y_pos),
        xytext=xytext,
        textcoords="offset points",
        fontsize=8,
        color=label_color,
        bbox=dict(facecolor="white", edgecolor=label_color, alpha=0.7),
    )

plt.title("Evolution of OD over Time by Condition")
plt.xlabel("Incubation Time")
plt.ylabel("OD")
plt.legend(title="Condition", bbox_to_anchor=(1.05, 1), loc="upper left")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
