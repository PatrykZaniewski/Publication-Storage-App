package Config;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.nio.charset.StandardCharsets;
import java.util.Date;

public class TokenHandler {
    public String listToken(String login)
    {
        return Jwts.builder()
                .setIssuer("desktop.app")
                .claim("exp", new Date(2147483647))
                .claim("uid", login)
                .claim("action", "list")
                .signWith(
                        SignatureAlgorithm.HS256,
                        "SECRET".getBytes(StandardCharsets.UTF_8)
                )
                .compact();
    }

    public String uploadToken(String login)
    {
        return Jwts.builder()
                .setIssuer("desktop.app")
                .claim("exp", new Date(2147483647))
                .claim("uid", login)
                .claim("action", "upload")
                .signWith(
                        SignatureAlgorithm.HS256,
                        "SECRET".getBytes(StandardCharsets.UTF_8)
                )
                .compact();
    }
}
