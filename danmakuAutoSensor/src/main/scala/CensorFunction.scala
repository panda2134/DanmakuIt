package site.panda2134.danmakuit

import org.json4s.DefaultFormats
import org.json4s.native.Serialization

import java.time._
import java.util.concurrent.CompletableFuture
import java.util.function.Function
import scala.concurrent.Future
import sttp.client3._
import sttp.client3.asynchttpclient.future.AsyncHttpClientFutureBackend
import sttp.client3.json4s._

import scala.concurrent.ExecutionContext.Implicits.global
import scala.jdk.FutureConverters._


class CensorFunction extends Function[String, CompletableFuture[String]] {
  private val APIKey = "***REMOVED***"
  private val SecretKey = "***REMOVED***"
  implicit val serialization: Serialization.type = org.json4s.native.Serialization
  implicit val formats: DefaultFormats.type = org.json4s.DefaultFormats
  implicit val sttpBackend: SttpBackend[Future, Any] = AsyncHttpClientFutureBackend()

  object fetchAccessToken extends (() => Future[String]) {
    private val expirationTime = Period.ofDays(10)
    private var lastFetchDateTime = new LocalDateTime(0)
    private var tokenCache = ""

    private case class AccessTokenResponse(access_token: String)

    override def apply(): Future[String] = {
      if (tokenCache == null ||
        ((lastFetchDateTime plus expirationTime) isBefore LocalDateTime.now())) {
        // fetch again
        for {
          req <- basicRequest
            .get(uri"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=$APIKey&client_secret=$SecretKey")
            .response(asJson[AccessTokenResponse])
            .send(sttpBackend)
        } yield {
          req.body match {
            case Right(tokenResponse: AccessTokenResponse) =>
              lastFetchDateTime = LocalDateTime.now()
              tokenCache = tokenResponse.access_token
            case Left(_) => println("Token update failed")
          }
          tokenCache
        }
      } else {
        Future(tokenCache)
      }
    }
  }

  def censorRemote(t: String): Future[Boolean] = {
    case class CensorResponse(conclusionType: Int)
    for {
      token <- fetchAccessToken()
      t <- basicRequest.post(uri"https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined?access_token=$token")
        .body(Map("text" -> t))
        .response(asJson[CensorResponse])
        .send(sttpBackend)
        .map(_.body match {
          case Right(censorResponse) => censorResponse.conclusionType == 1
          case Left(_) => false
        })
    } yield t
  }
//
//  def censorCustom(t: string): Future[Boolean] = {
//
//  }

  def censorAll(t: String): Future[Boolean] = censorRemote(t)

  override def apply(t: String): CompletableFuture[String] = {
    censorAll(t).map(if (_) t else "").asJava.toCompletableFuture
  }
}
