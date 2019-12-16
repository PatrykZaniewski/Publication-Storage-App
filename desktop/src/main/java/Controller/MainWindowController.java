package Controller;

import Config.RedisHandler;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.MenuBar;
import javafx.scene.image.Image;
import javafx.stage.Stage;

import java.io.IOException;

public class MainWindowController {

    @FXML
    public javafx.scene.control.MenuBar MenuBar;

    private String login;
    private RedisHandler redisHandler;

    public void setLogin(String login) {
        this.login = login;
    }

    public void setRedisHandler(RedisHandler redisHandler)
    {
        this.redisHandler = redisHandler;
    }


    public void quit(ActionEvent actionEvent) {
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
}
