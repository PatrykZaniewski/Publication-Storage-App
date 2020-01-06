package Controller;

import Config.RedisHandler;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.MenuBar;
import javafx.scene.control.ScrollPane;
import javafx.scene.image.Image;
import javafx.stage.Stage;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.ProtocolException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Date;

public class MainWindowController {

    @FXML
    public javafx.scene.control.MenuBar MenuBar;
    public ScrollPane pubPane;

    private String login;
    private RedisHandler redisHandler;

    public void setLogin(String login) {
        this.login = login;

    }

    public void setRedisHandler(RedisHandler redisHandler)
    {
        this.redisHandler = redisHandler;
    }

    public void getData(){
        try {
            String jwt = Jwts.builder()
                    .setIssuer("desktop.app")
                    .claim("exp", new Date(2147483647))
                    .claim("uid", login)
                    .claim("action", "list")
                    .signWith(
                            SignatureAlgorithm.HS256,
                            "SECRET".getBytes(StandardCharsets.UTF_8)
                    )
                    .compact();
            System.out.println(jwt);

            URL url = new URL("http://localhost:5002/list/" + login + "?token=" + jwt);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("GET");

            BufferedReader in = new BufferedReader(new InputStreamReader(
                    con.getInputStream()));
            String inputLine;
            while ((inputLine = in.readLine()) != null) {
                System.out.println(inputLine);
            }
            in.close();
        }
        catch (IOException e)
        {
            System.out.println(e);
        }
    }

    public void afterLoad(){
        getData();
    }


    public void quit(ActionEvent actionEvent) {
        redisHandler.deleteRedisRecord(login);
        System.out.println(login);
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
