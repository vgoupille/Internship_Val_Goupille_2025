#!/usr/bin/env python3
"""
Script de validation de la configuration du pipeline MultiQC
Vérifie que tous les fichiers et dépendances sont présents
"""

import os
import sys
import yaml
import argparse
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists and report status"""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} - MANQUANT")
        return False


def check_yaml_format(yaml_file):
    """Check YAML file format and content"""
    try:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        if "samples" not in data:
            print(f"✗ Format YAML: Clé 'samples' manquante dans {yaml_file}")
            return False

        sample_count = len(data["samples"])
        print(f"✓ Format YAML: {sample_count} échantillons trouvés")

        # Check at least one sample has R1 and R2 data
        for sample_name, sample_data in data["samples"].items():
            if "R1" not in sample_data or "R2" not in sample_data:
                print(
                    f"✗ Format YAML: L'échantillon {sample_name} n'a pas de données R1/R2"
                )
                return False
            break

        return True

    except Exception as e:
        print(f"✗ Format YAML: Erreur lors de la lecture de {yaml_file}: {e}")
        return False


def check_fastq_files(yaml_file, data_type=None, max_check=3):
    """Check if FASTQ files exist (sample a few files)"""
    try:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        checked_files = 0
        missing_files = 0

        for sample_name, sample_data in data["samples"].items():
            if checked_files >= max_check:
                break

            for read_type in ["R1", "R2"]:
                if data_type and data_type in sample_data[read_type]:
                    file_path = sample_data[read_type][data_type]
                    if os.path.exists(file_path):
                        print(f"✓ Fichier FASTQ: {file_path}")
                    else:
                        print(f"✗ Fichier FASTQ: {file_path} - MANQUANT")
                        missing_files += 1
                    checked_files += 1

        if missing_files == 0:
            print(f"✓ Tous les fichiers FASTQ vérifiés ({checked_files}) sont présents")
            return True
        else:
            print(
                f"✗ {missing_files} fichiers FASTQ manquants sur {checked_files} vérifiés"
            )
            return False

    except Exception as e:
        print(f"✗ Erreur lors de la vérification des fichiers FASTQ: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Valider la configuration du pipeline MultiQC"
    )
    parser.add_argument("--data_type", help="Type de données à vérifier (optionnel)")
    parser.add_argument(
        "--check_fastq",
        action="store_true",
        help="Vérifier l'existence des fichiers FASTQ",
    )
    args = parser.parse_args()

    print("=== Validation du Pipeline MultiQC ===\n")

    # Get script directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent.parent.parent

    # Define paths
    paths = {
        "Script principal": script_dir / "launch_multiQC_jobs.sh",
        "Script SLURM": script_dir / "run_multiQC.sh",
        "Script Python": script_dir / "run_multiQC.py",
        "Environnement conda": script_dir / "environment_multiQC.yml",
        "Script création env": script_dir / "create_env_multiQC.sh",
        "README": script_dir / "README.md",
        "Fichier YAML échantillons": project_dir
        / "data/info/samples/samples_trimming.yaml",
    }

    print("1. Vérification des fichiers du pipeline:")
    all_files_exist = True
    for description, path in paths.items():
        if not check_file_exists(path, description):
            all_files_exist = False

    print("\n2. Vérification du format YAML:")
    yaml_file = paths["Fichier YAML échantillons"]
    yaml_valid = False
    if os.path.exists(yaml_file):
        yaml_valid = check_yaml_format(yaml_file)

    print("\n3. Vérification des répertoires:")
    dirs_to_check = [
        (project_dir / "data/processed_data", "Répertoire de sortie par défaut"),
        (script_dir / "logs", "Répertoire des logs"),
    ]

    for dir_path, description in dirs_to_check:
        if dir_path.exists():
            print(f"✓ {description}: {dir_path}")
        else:
            print(f"? {description}: {dir_path} - sera créé automatiquement")

    # Check FASTQ files if requested
    if args.check_fastq and args.data_type and yaml_valid:
        print(f"\n4. Vérification des fichiers FASTQ ({args.data_type}):")
        check_fastq_files(yaml_file, args.data_type)

    # Summary
    print("\n=== Résumé de la validation ===")
    if all_files_exist:
        print("✓ Tous les fichiers du pipeline sont présents")
    else:
        print("✗ Certains fichiers du pipeline sont manquants")

    if yaml_valid:
        print("✓ Le fichier YAML est valide")
    else:
        print("✗ Le fichier YAML a des problèmes")

    # Exit status
    if all_files_exist and yaml_valid:
        print("\n🎉 Le pipeline est prêt à être utilisé !")
        sys.exit(0)
    else:
        print(
            "\n⚠️  Des problèmes ont été détectés. Veuillez les corriger avant d'utiliser le pipeline."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
