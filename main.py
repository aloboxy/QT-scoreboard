import sys,shutil,time,os
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QMessageBox, QLabel, QPushButton, QFileDialog, QWidget, QHBoxLayout,QLineEdit
from PyQt5.QtCore import Qt, QTimer,QUrl,QDir
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent,QSound
from PyQt5.QtGui import QPixmap
from database import save_match, get_matches, get_teams, save_team, delete_team,get_team_by_id,save_match
from new import Ui_MainWindow

class TeamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.load_teams()
        # self.load_match_history()

        self.ui.uploadLogoButton.clicked.connect(self.upload_logo)
        self.ui.addTeamButton.clicked.connect(self.add_team)
        self.ui.start_timer.clicked.connect(self.start_timer)
        self.ui.reset_timer.clicked.connect(self.reset_timer)
        self.ui.reset.clicked.connect(self.reset_game)

        # self.ui.checkBox.setStyleSheet("QCheckBox::indicator {width:25px; height:25px;}")
        # self.ui.checkBox_3.setStyleSheet("QCheckBox::indicator {width:25px; height:25px;}")
        # self.ui.checkBox_2.setStyleSheet("QCheckBox::indicator {width:25px; height:25px;}")
        # self.ui.checkBox_4.setStyleSheet("QCheckBox::indicator {width:25px; height:25px;}")
        # self.ui.checkBox_5.setStyleSheet("QCheckBox::indicator {width:25px; height:25px;}")
        # self.ui.checkBox_6.setStyleSheet("QCheckBox::indicator {width:25px; height:25px;}")


        # Initialize scores
        self.team1_score = 0
        self.team2_score = 0

        # Score buttons
        self.ui.team1_10.clicked.connect(lambda: self.update_score(1, 10))
        self.ui.team1_15.clicked.connect(lambda: self.update_score(1, 15))
        self.ui.team1_minus_5.clicked.connect(lambda: self.update_score(1, -5))
        self.ui.team2_10.clicked.connect(lambda: self.update_score(2, 10))
        self.ui.team2_15.clicked.connect(lambda: self.update_score(2, 15))
        self.ui.team2_minus_5.clicked.connect(lambda: self.update_score(2, -5))

        self.tick_player = QMediaPlayer()
        self.tick_player = QSound("assets/slow-tick.wav")
        # self.tick_player.setMedia(QMediaContent(QUrl.fromLocalFile(sound_path)))

        self.alarm_player = QMediaPlayer()
        sound_path = QDir.current().absoluteFilePath("assets/timer.mp3")
        self.alarm_player.setMedia(QMediaContent(QUrl.fromLocalFile(sound_path)))

    def reset_game(self):
        reply = QMessageBox.information(self, "Warning", "Are You sure you want to reset this game?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        else:
            self.ui.teamname_live2_2.clear()
            self.ui.teamname_live2.clear()
            self.ui.team1_score.setText("0")
            self.ui.team2_score.setText("0")
            self.ui.Margin.setText("0")
            self.team1_score = 0
            self.team2_score = 0
            self.Margin = 0

    def update_score(self, team, change):
        """Update team scores and calculate margin."""
        if team == 1:
            self.team1_score = max(-1500, self.team1_score + change)
            self.ui.team1_score.setText(str(self.team1_score))
        else:
            self.team2_score = max(-1500, self.team2_score + change)
            self.ui.team2_score.setText(str(self.team2_score))

        margin = abs(self.team1_score - self.team2_score)
        self.ui.Margin.setText(f"{margin}")

    def reset_scores(self):
        """Save match before resetting scores."""
        save_match("Team 1", "Team 2", self.team1_score, self.team2_score, abs(self.team1_score - self.team2_score))
        self.load_match_history()

        self.team1_score = 0
        self.team2_score = 0
        self.ui.team1_score.setText("0")
        self.ui.team2_score.setText("0")
        self.ui.Margin.setText("0")

    def load_match_history(self):
        """Load match history."""
        matches = get_matches()
        self.ui.tableWidget_2.setRowCount(len(matches))
        for row, match in enumerate(matches):
            for col, data in enumerate(match):
                self.ui.TournamentName.setItem(row, col, QTableWidgetItem(str(data)))

    def load_teams(self):
        """Loads teams from the database."""
        teams = get_teams()
        self.ui.teamTable.setRowCount(len(teams))

        for row, team in enumerate(teams):
            team_item = QTableWidgetItem(team[1])
            team_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.ui.teamTable.setItem(row, 0, team_item)

            label = QLabel()
            pixmap = QPixmap(team[2])
            label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.ui.teamTable.setCellWidget(row, 1, label)

            action_widget = QWidget()
            layout = QHBoxLayout(action_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")
            edit_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
            delete_button.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")

            delete_button.clicked.connect(lambda _, team_id=team[0]: self.delete_team(team_id))

            layout.addWidget(edit_button)
            layout.addWidget(delete_button)
            action_widget.setLayout(layout)
            self.ui.teamTable.setCellWidget(row, 2, action_widget)


    def delete_team(self, team_id):
        reply = QMessageBox.information(self, "Warning", "Are You sure you want to delete this team?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
        else:
            team = get_team_by_id(team_id)  # Fetch the team by ID
            logo_path = team[2]  # Assuming the 3rd column contains the logo path
            if os.path.exists(logo_path):
                try:
                    os.remove(logo_path)  # Remove the logo file
                    print(f"Deleted logo file: {logo_path}")
                except Exception as e:
                    print(f"Error deleting logo file: {e}")
            # Delete the team from the database
            delete_team(team_id)
            # Reload the team list
            self.load_teams()
            self.team1_dropdown()



    def upload_logo(self):
        """Upload team logo and copy it to assets folder."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Team Logo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            filename = os.path.basename(file_path)
            destination = os.path.join("assets", filename)

            try:
                shutil.copy(file_path, destination)  # Copy image to assets folder
                pixmap = QPixmap(destination)
                self.ui.teamLogoLabel.setPixmap(pixmap.scaled(100, 100))
                self.ui.teamLogoPath.setText(destination)  # Save relative path to DB
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to copy image: {str(e)}")


    def add_team(self):
        """Add new team."""
        team_name = self.ui.teamNameInput.text()
        logo_path = self.ui.teamLogoPath.text()

        if not team_name:
            QMessageBox.warning(self, "Error", "Enter team name and upload logo!")
            return

        save_team(team_name, logo_path)
        self.load_teams()
        self.team1_dropdown()

        QMessageBox.information(self, "Success", "Team added successfully!")
        self.ui.teamNameInput.clear()
        self.ui.teamLogoLabel.clear()
        self.ui.teamLogoPath.clear()


    def create_match(self):
        """Create a match."""
        team1 = self.ui.team1_name.text()
        team2 = self.ui.team2_name.text()
        score1 = int(self.ui.team1_score.text())
        score2 = int(self.ui.team2_score.text())
        margin = abs(score1 - score2)

        if not team1 or not team2:
            QMessageBox.warning(self, "Error", "Enter team names!")
            return

        save_match(team1, team2, score1, score2, margin)
        self.load_match_history()

        QMessageBox.information(self, "Success", "Match created successfully!")
        self.ui.team1_name.clear()
        self.ui.team2_name.clear()
        self.ui.team1_score.clear()
        self.ui.team2_score.clear()
        self.ui.Margin.clear()



    def start_timer(self):
        """Start countdown based on user input"""
        text = self.ui.lineEdit_2.text()
        if not text.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of seconds.")
            return
        self.remaining_time = int(text)
        self.ui.count_down_2.setText(self.format_time(self.remaining_time))
        self.ui.count_down.setText(self.format_time(self.remaining_time))
        self.alarm_player.stop()
        self.tick_player.stop()
        self.timer.start(1000)  # Trigger every 1 second

    def reset_timer(self):
        """Reset timer to user input value"""
        self.timer.stop()
        self.alarm_player.stop()
        self.tick_player.stop()
      
        text = self.ui.lineEdit_2.text()
        if not text.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of seconds.")
            return
        self.remaining_time = int(text)
        self.ui.count_down_2.setText(self.format_time(self.remaining_time))
        self.ui.count_down.setText(self.format_time(self.remaining_time))
         # Trigger every 1 second

    def update_timer(self):
        """Update timer countdown"""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.ui.count_down_2.setText(self.format_time(self.remaining_time))
            self.ui.count_down.setText(self.format_time(self.remaining_time)) # ensure it starts from beginning
            self.tick_player.play()
        else:
            self.timer.stop()
            self.ui.count_down_2.setText("TIME UP!")
            self.ui.count_down.setText("TIME UP!")
            self.alarm_player.stop()
            self.tick_player.stop()   # ensure it starts from beginning
            self.alarm_player.play()
            # Play alarm sound

    def stop_timer(self):
        """Pause the timer"""
        self.timer.stop()


    def format_time(self, seconds):
        """Convert seconds to MM:SS format"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02}:{secs:02}"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TeamApp()
    window.show()
    sys.exit(app.exec_())