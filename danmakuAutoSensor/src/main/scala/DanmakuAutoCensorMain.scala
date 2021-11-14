package site.panda2134.danmakuit

import scala.jdk.FunctionConverters._
import scala.jdk.FutureConverters._
import scala.concurrent.ExecutionContext.Implicits.global

object DanmakuAutoCensorMain extends App{
  val censorFunc = new CensorFunction
  for {
    res1 <- censorFunc.censorAll("测试内容")
    res2 <- censorFunc.censorAll("博彩澳门美女荷官发牌")
  } {
    println("Expected true", res1)
    println("Expected false", res2)
  }
}
