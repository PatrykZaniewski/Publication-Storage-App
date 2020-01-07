package Controller;

import Config.MultipartRequest;
import javafx.event.ActionEvent;
import javafx.scene.control.Alert;
import javafx.scene.control.DatePicker;
import javafx.scene.control.TextField;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import java.io.*;
import java.util.List;


public class AddPublication {
    public TextField authorField;
    public TextField titleField;
    public TextField publisherField;
    public DatePicker dateField;

    private List<File> files;
    private String login;
    private String uploadToken;

    public void setLogin(String login) {
        this.login = login;
    }

    public void setUploadToken(String uploadToken) {
        this.uploadToken = uploadToken;
    }

    public void addFiles(ActionEvent actionEvent) {
        FileChooser chooser = new FileChooser();
        chooser.setTitle("Wybierz plik do wczytania");
        files = chooser.showOpenMultipleDialog(authorField.getScene().getWindow());
    }


    public void returnMain(ActionEvent actionEvent) {
        Stage currStage = (Stage) authorField.getScene().getWindow();
        currStage.close();
    }

    public void addPublication(ActionEvent actionEvent) {
        if (authorField.getText().equals("") || titleField.getText().equals("") || publisherField.getText().equals("") || dateField.getValue() == null) {
            Alert alert = new Alert(Alert.AlertType.ERROR);
            alert.setTitle("Błąd");
            alert.setHeaderText("Błąd");
            alert.setContentText("Wypełnij wszystkie pola!");
            alert.showAndWait();
        } else {
            try {
                MultipartRequest multipartRequest = new MultipartRequest("http://localhost:5002/list", "UTF-8");
                multipartRequest.addFormField("uid", login);
                multipartRequest.addFormField("author", authorField.getText());
                multipartRequest.addFormField("title", titleField.getText());
                multipartRequest.addFormField("publisher", publisherField.getText());
                multipartRequest.addFormField("publishDate", String.valueOf(dateField.getValue()));
                multipartRequest.addFormField("token", uploadToken);

                if (files != null) {
                    for (File file : files) {
                        multipartRequest.addFilePart("files", file);
                    }
                }

                int response = multipartRequest.finish();
                if(response == 200)
                {
                    Alert alert = new Alert(Alert.AlertType.INFORMATION);
                    alert.setTitle("Dodawanie publikacji");
                    alert.setHeaderText(null);
                    alert.setContentText("Publikacja dodana pomyślnie");
                    alert.showAndWait();
                    Stage currStage = (Stage) authorField.getScene().getWindow();
                    currStage.close();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
