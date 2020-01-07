package Controller;

import Config.MultipartRequest;
import javafx.event.ActionEvent;
import javafx.scene.control.Alert;
import javafx.scene.control.DatePicker;
import javafx.scene.control.TextField;
import javafx.stage.Stage;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;

public class EditPublication {
    public TextField authorField;
    public TextField publisherField;
    public TextField titleField;
    public DatePicker dateField;

    private String login;
    private String editToken;
    private int publicationId;
    private String author;
    private String title;
    private String publisher;
    private String date;

    public void setLogin(String login) {
        this.login = login;
    }

    public void setEditToken(String editToken) {
        this.editToken = editToken;
    }

    public void setPublicationId(int publicationId) {
        this.publicationId = publicationId;
    }

    public void returnDetails(ActionEvent actionEvent) {
        Stage currStage = (Stage) authorField.getScene().getWindow();
        currStage.close();
    }

    public void updatePublication(ActionEvent actionEvent) {
        try {
            MultipartRequest multipartRequest = new MultipartRequest("http://localhost:5002/updlist/" + login + "/" + publicationId, "UTF-8");
            multipartRequest.addFormField("author", authorField.getText());
            multipartRequest.addFormField("title", titleField.getText());
            multipartRequest.addFormField("publisher", publisherField.getText());
            multipartRequest.addFormField("publishDate", String.valueOf(dateField.getValue()));
            multipartRequest.addFormField("token", editToken);

            int response = multipartRequest.finish();
            if (response == 200) {
                Alert alert = new Alert(Alert.AlertType.INFORMATION);
                alert.setTitle("Uaktualnianie publikacji");
                alert.setHeaderText(null);
                alert.setContentText("Publikacja uaktualniona pomyślnie");
                alert.showAndWait();
                Stage currStage = (Stage) authorField.getScene().getWindow();
                currStage.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void setData(String author, String title, String publisher, String date) {
        this.author = author;
        this.title = title;
        this.publisher = publisher;
        this.date = date;
    }

    public void afterLoad() {
        displayData();
    }

    public void displayData() {
        authorField.setText(author);
        titleField.setText(title);
        publisherField.setText(publisher);
        dateField.setValue(LocalDate.parse(date));
    }
}
