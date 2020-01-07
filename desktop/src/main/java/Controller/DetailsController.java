package Controller;

import Config.MultipartRequest;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;
import javafx.stage.FileChooser;
import javafx.stage.Modality;
import javafx.stage.Stage;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Arrays;
import java.util.List;

public class DetailsController {

    public TextField authorField;
    public TextField publisherField;
    public TextField dateField;
    public TextField titleField;
    public ScrollPane filesPane;

    private String login;
    private int publicationId;
    private String listToken;
    private String uploadToken;
    private String deleteToken;
    private String editToken;
    private JSONObject dataJson;

    public void setLogin(String login) {
        this.login = login;
    }

    public void setPublicationId(int publicationId) {
        this.publicationId = publicationId;
    }

    public void setListToken(String listToken) {
        this.listToken = listToken;
    }

    public void setUploadToken(String uploadToken) {
        this.uploadToken = uploadToken;
    }

    public void setDeleteToken(String deleteToken) {
        this.deleteToken = deleteToken;
    }

    public void setEditToken(String editToken) {
        this.editToken = editToken;
    }

    public void afterLoad() {
        getData();
    }

    public void getData() {
        try {
            URL url = new URL("http://localhost:5002/list/" + login + "/" + publicationId + "?token=" + listToken);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET");

            InputStreamReader inputStreamReader;

            if (con.getResponseCode() == 200) {
                inputStreamReader = new InputStreamReader(con.getInputStream());
            } else {
                inputStreamReader = new InputStreamReader(con.getErrorStream());
            }
            StringBuilder message = new StringBuilder();
            BufferedReader in = new BufferedReader(inputStreamReader);
            String inputLine;
            while ((inputLine = in.readLine()) != null) {
                message.append(inputLine);
            }
            in.close();
            String messageString = message.toString();
            if (con.getResponseCode() == 200) {
                dataJson = new JSONObject(messageString);
            } else {
                errorMessage(messageString);
            }
            displayData();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void displayData() {
        JSONObject detailsData = new JSONObject((String) dataJson.get("details"));
        authorField.setText((String) detailsData.get("author"));
        titleField.setText((String) detailsData.get("title"));
        publisherField.setText((String) detailsData.get("publisher"));
        dateField.setText((String) detailsData.get("publishDate"));

        String filesString = (String) dataJson.get("files");
        filesString = filesString.replace("\"", "");
        List<String> filesList = Arrays.asList(filesString.substring(1, filesString.length() - 1).split(","));
        VBox vbox = new VBox();
        if (filesList.size() > 0 && !filesList.get(0).equals("")) {
            for (String filename : filesList) {
                HBox hbox = new HBox();
                Label fileLink = new Label(filename);
                fileLink.setStyle("-fx-underline: true; -fx-text-fill: #0000ff");
                fileLink.setOnMouseClicked(event -> {
                    downloadFile(filename);
                });
                Label fileDelete = new Label("        Usuń");
                fileDelete.setOnMouseClicked(event -> {
                    deleteFile(filename);
                });
                fileDelete.setStyle("-fx-text-fill: #ff0000");
                hbox.getChildren().addAll(fileLink, fileDelete);
                hbox.setAlignment(Pos.CENTER);
                hbox.setPadding(new Insets(5, 30, 5, 30));
                vbox.getChildren().addAll(hbox);
            }
            vbox.setSpacing(5);
            vbox.setPadding(new Insets(10));
            filesPane.setContent(vbox);
            filesPane.setPannable(true);
        }
    }

    public void downloadFile(String filename) {
        System.out.println(filename);
    }

    public void deleteFile(String filename) {
        try {
            MultipartRequest multipartRequest = new MultipartRequest("http://localhost:5002/delfiles/" + login + "/" + publicationId + "?token=" + deleteToken + "&filename=" + filename, "UTF-8");
            int response = multipartRequest.finish();
            if (response == 200) {
                getData();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void errorMessage(String message) {
        System.out.println(message);
    }

    public void closeDetails(ActionEvent actionEvent) {
        Stage currStage = (Stage) authorField.getScene().getWindow();
        currStage.close();
    }

    public void editDetails(ActionEvent actionEvent) {
        try {
            Stage stage = new Stage();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/FXML/editPublication.fxml"));
            Parent root = loader.load();

            JSONObject detailsData = new JSONObject((String) dataJson.get("details"));

            EditPublication editPublication = loader.getController();
            editPublication.setLogin(login);
            editPublication.setPublicationId(publicationId);
            editPublication.setEditToken(editToken);
            editPublication.setData((String) detailsData.get("author"), (String) detailsData.get("title"), (String) detailsData.get("publisher"), (String) detailsData.get("publishDate"));
            editPublication.afterLoad();

            stage.setTitle("Publication Storage");
            stage.setScene(new Scene(root, 400, 200));
            stage.setResizable(false);
            Image icon = new Image("Icons/icon.png");
            stage.getIcons().add(icon);
            stage.setResizable(false);
            stage.initOwner(authorField.getScene().getWindow());
            stage.initModality(Modality.WINDOW_MODAL);
            stage.showAndWait();
            getData();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void addFiles(ActionEvent actionEvent) {
        FileChooser chooser = new FileChooser();
        chooser.setTitle("Wybierz plik do wczytania");
        List<File> files = chooser.showOpenMultipleDialog(authorField.getScene().getWindow());

        if (files.size() > 0) {
            try {
                MultipartRequest multipartRequest = new MultipartRequest("http://localhost:5002/files/" + login + "/" + publicationId + "?token=" + uploadToken, "UTF-8");
                for (File file : files) {
                    multipartRequest.addFilePart("files", file);
                }
                int response = multipartRequest.finish();
                if (response == 200) {
                    Alert alert = new Alert(Alert.AlertType.INFORMATION);
                    alert.setTitle("Dodawanie plików");
                    alert.setHeaderText(null);
                    alert.setContentText("Pliki zostały załączone!");
                    alert.showAndWait();
                    getData();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }


    }

    public void deletePublication(ActionEvent actionEvent) {
        try {
            MultipartRequest multipartRequest = new MultipartRequest("http://localhost:5002/dellist/" + login + "/" + publicationId + "?token=" + deleteToken, "UTF-8");
            int response = multipartRequest.finish();
            if (response == 200) {
                Stage currStage = (Stage) authorField.getScene().getWindow();
                currStage.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
