package Controller;

import Config.RedisHandler;
import Config.TokenHandler;
import Model.BasicData;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.TableCell;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.stage.Modality;
import javafx.stage.Stage;
import javafx.util.Callback;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Set;

public class MainWindowController {

    @FXML
    public javafx.scene.control.MenuBar MenuBar;
    @FXML
    public TableView<BasicData> displayTable;
    @FXML
    public TableColumn<BasicData, Integer> id;
    @FXML
    public TableColumn<BasicData, String> title;

    private String login;
    private RedisHandler redisHandler;
    private String listToken;
    private String uploadToken;
    private String deleteToken;
    private String editToken;
    private JSONObject dataJson;

    public void setLogin(String login) {
        this.login = login;
    }

    public void setRedisHandler(RedisHandler redisHandler) {
        this.redisHandler = redisHandler;
    }


    @FXML
    public void initialize() {
        id.setCellValueFactory(new PropertyValueFactory<>("Id"));
        title.setCellValueFactory(new PropertyValueFactory<>("Title"));
    }

    public void generateTokens() {
        TokenHandler tokenHandler = new TokenHandler();
        listToken = tokenHandler.listToken(login);
        uploadToken = tokenHandler.uploadToken(login);
        deleteToken = tokenHandler.deleteToken(login);
        editToken = tokenHandler.editToken(login);
    }

    public void getData() {
        try {
            URL url = new URL("http://localhost:5002/list/" + login + "?token=" + listToken);
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

    public void errorMessage(String message) {
        System.out.println(message);
    }

    public void afterLoad() {
        generateTokens();
        getData();
    }

    public void displayData() {
        Set<String> keys = dataJson.keySet();
        ObservableList<BasicData> basicData = FXCollections.observableArrayList();

        for (String key : keys) {
            if (!key.equals("_links")) {
                BasicData bs = new BasicData(Integer.parseInt(key), (String) dataJson.get(key));
                basicData.add(bs);
            }
        }
        displayTable.setItems(basicData);
        addButtons();
    }

    public void displayDetail(int id) {
        try {
            Stage stage = new Stage();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/FXML/publicationDetails.fxml"));
            Parent root = loader.load();

            DetailsController detailsController = loader.getController();
            detailsController.setLogin(login);
            detailsController.setPublicationId(id);
            detailsController.setListToken(listToken);
            detailsController.setUploadToken(uploadToken);
            detailsController.setDeleteToken(deleteToken);
            detailsController.setEditToken(editToken);
            detailsController.afterLoad();

            stage.setTitle("Publication Storage");
            stage.setScene(new Scene(root, 400, 300));
            stage.setResizable(false);
            Image icon = new Image("Icons/icon.png");
            stage.getIcons().add(icon);
            stage.setResizable(false);
            stage.initOwner(MenuBar.getScene().getWindow());
            stage.initModality(Modality.WINDOW_MODAL);
            stage.showAndWait();
            getData();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void addButtons() {
        TableColumn<BasicData, Void> colBtn = new TableColumn("Wyświetl");

        Callback<TableColumn<BasicData, Void>, TableCell<BasicData, Void>> cellFactory = new Callback<TableColumn<BasicData, Void>, TableCell<BasicData, Void>>() {
            @Override
            public TableCell<BasicData, Void> call(final TableColumn<BasicData, Void> param) {
                final TableCell<BasicData, Void> cell = new TableCell<BasicData, Void>() {

                    private final Button btn = new Button("Wybierz");

                    {
                        btn.setOnAction((ActionEvent event) -> {
                            BasicData data = getTableView().getItems().get(getIndex());
                            displayDetail(data.getId());
                        });
                    }

                    @Override
                    public void updateItem(Void item, boolean empty) {
                        super.updateItem(item, empty);
                        if (empty) {
                            setGraphic(null);
                        } else {
                            setGraphic(btn);
                        }
                    }
                };
                return cell;
            }
        };

        colBtn.setCellFactory(cellFactory);
        displayTable.getColumns().add(colBtn);
    }

    public void quit(ActionEvent actionEvent) {
        redisHandler.deleteRedisRecord(login);
        Platform.exit();
        System.exit(0);
    }

    public void logout(ActionEvent actionEvent) throws IOException {
        redisHandler.deleteRedisRecord(login);

        Stage stage = new Stage();
        Parent root = FXMLLoader.load(getClass().getResource("/FXML/login.fxml"));
        stage.setTitle("Publication Storage");
        stage.setScene(new Scene(root, 300, 175));
        Image icon = new Image("Icons/icon.png");
        stage.getIcons().add(icon);
        stage.setResizable(false);
        stage.show();

        Stage currStage = (Stage) MenuBar.getScene().getWindow();
        currStage.close();
    }

    public void addPublication(ActionEvent actionEvent) throws IOException {
        Stage stage = new Stage();
        FXMLLoader loader = new FXMLLoader(getClass().getResource("/FXML/addPublication.fxml"));
        Parent root = loader.load();

        AddPublication addPublication = loader.getController();
        addPublication.setLogin(login);
        addPublication.setUploadToken(uploadToken);

        stage.setTitle("Publication Storage");
        stage.setScene(new Scene(root, 400, 200));
        stage.setResizable(false);
        Image icon = new Image("Icons/icon.png");
        stage.getIcons().add(icon);
        stage.setResizable(false);
        stage.initOwner(MenuBar.getScene().getWindow());
        stage.initModality(Modality.WINDOW_MODAL);
        stage.showAndWait();
        getData();
    }
}