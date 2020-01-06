package Controller;

import javafx.fxml.FXML;
import javafx.scene.control.DatePicker;
import javafx.scene.control.TextField;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class DetailsController {

    public TextField authorField;
    public TextField publisherField;
    public TextField dateField;
    public TextField titleField;

    private String login;
    private int publicationId;
    private String listToken;
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
    }

    public void errorMessage(String message) {
        System.out.println(message);
    }
}
