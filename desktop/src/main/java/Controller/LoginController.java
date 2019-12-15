package Controller;

import Config.RedisHandler;
import javafx.fxml.FXML;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.PasswordField;
import javafx.scene.control.TextField;
import javafx.scene.input.MouseEvent;

public class LoginController {

    @FXML
    public Button loginButton;
    public TextField loginField;
    public PasswordField passwordField;
    public Label errorLabel;

    private RedisHandler redisHandler;

    @FXML
    void initialize()
    {
        redisHandler = new RedisHandler("localhost", 6379);
    }


    public void submit(MouseEvent mouseEvent) {
        if (!passwordField.getText().equals("") && !loginField.getText().equals("")) {
            if (redisHandler.checkData(loginField.getText(), passwordField.getText()) == 0) {
                System.out.println("XD");
            } else if (redisHandler.checkData(loginField.getText(), passwordField.getText()) == 1) {
                errorLabel.setText("Nieprawidłowe dane logowania!");
            }
            else
            {
                errorLabel.setText("Wystąpił problem z połączeniem!");
            }
        }
        else
        {
            errorLabel.setText("Wypełnij wszystkie pola!");
        }
    }
}
