# LED 模块踩坑

---

## 坑 1：Timer2 中断中使用 32 位取模导致软件 I2C 时序崩溃

> 第十三届国赛 · 发现者：左岚

### 现象

与 Timer2 中断共用软件 I2C 总线的传感器（如 AHT10）读数异常：输出为 0，或数值随机乱跳，但代码逻辑看起来没有问题。

### 原因

Timer2 每 100μs 中断一次用于 PWM 计数，中断里用 `unsigned long int` 做 32 位取模，8051 需调用库函数，耗时是 `unsigned char` 自增比较的 **10 倍以上**。中断频繁打断软件模拟 I2C 的 SDA/SCL 操作，破坏位时序，导致从机误判：

```c
// 错误写法：32 位取模在 8051 上调用库函数，中断耗时大幅增加
idata unsigned long int pwm;

// ISR 内
pwm = (++pwm) % 10;
```

### 解决方法

换成 `unsigned char`，用条件归零代替取模：

```c
// 正确写法：2~3 条指令，中断耗时 < 1μs
idata unsigned char PWM_Count = 0;

// ISR 内
if (++PWM_Count == 10) PWM_Count = 0;
```

### 举一反三

- ISR 应尽可能短，避免 32 位运算、除法、浮点运算、库函数调用
- 软件模拟 I2C / SPI 对中断延迟极敏感，与中断共用总线时要特别评估 ISR 执行时间
- PWM 计数变量用 `unsigned char` 足够（0～255），无需更大类型
